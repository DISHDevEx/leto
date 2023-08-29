import os
import sys
import subprocess
import joblib
import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path
import time
import boto3

root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality

def download_model(s3_args, method_args):
        """
        Downloads two model files from s3 to a local path.

        Parameters
        ----------
        s3_args: dict
            Defines the s3 bucket params.
        method_args: dict
            Defines reduction technique specific args.
        """
        s3 = boto3.client("s3")
        # print(s3)
        with open(method_args['encoder_model_path'], "wb") as file:
            # print(type(method_args['encoder_model_path']))
            # print(type(s3_args['model_bucket_s3']))
            # print(type(method_args['encoder_model_prefix_s3']))
            # print(file)
            s3.download_fileobj(s3_args['model_bucket_s3'], method_args['encoder_model_prefix_s3'], file)

        with open(method_args['decoder_model_path'], "wb") as file:
            s3.download_fileobj(s3_args['model_bucket_s3'], method_args['decoder_model_prefix_s3'], file)

def load_graph(frozen_graph_filename):
    """
    Function to load tensorflow model graph from a file.

    Parameters
    ----------
        frozen_graph_filename: string
            filename of frozen TensorFlow graph

    Returns
    ----------
        graph: TensorFlow graph
            pre-trained TensorFlow mdoel graph
    """
    with tf.io.gfile.GFile(frozen_graph_filename, "rb") as file:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(file.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)
    return graph

def encoder(image1, image2, features_folder, encoder_model_path):
    """
    Function to encode video frames into features and save these features into pickle files.

    Parameters
    ----------
        image1: numpy.ndarray
            image in the form of numpy array
        image2: numpy.ndarray
            image in the form of numpy array
        features_folder: string
            folder path to save encoded features in the form of pickle files
    """
    graph = load_graph(encoder_model_path)

    prefix = 'import/build_towers/tower_0/train_net_inference_one_pass/train_net/'
    Res = graph.get_tensor_by_name(prefix + 'Residual_Feature:0')
    inputImage = graph.get_tensor_by_name('import/input_image:0')
    previousImage = graph.get_tensor_by_name('import/input_image_ref:0')
    Res_prior = graph.get_tensor_by_name(prefix + 'Residual_Prior_Feature:0')
    motion = graph.get_tensor_by_name(prefix + 'Motion_Feature:0')
    bpp = graph.get_tensor_by_name(prefix + 'rate/Estimated_Bpp:0')
    psnr = graph.get_tensor_by_name(prefix + 'distortion/PSNR:0')
    reconframe = graph.get_tensor_by_name(prefix + 'ReconFrame:0')

    with tf.compat.v1.Session(graph=graph) as sess:
        dim = (1664, 896)
        image1 = cv2.resize(image1, dim, interpolation = cv2.INTER_LANCZOS4)
        image2 = cv2.resize(image2, dim, interpolation = cv2.INTER_LANCZOS4)
        image1 = image1 / 255.0
        image2 = image2 / 255.0
        image1 = np.expand_dims(image1, axis=0)
        image2 = np.expand_dims(image2, axis=0)

        bpp_est, Res_q, Res_prior_q, motion_q, psnr_val, recon_val = sess.run(
            [bpp, Res, Res_prior, motion, psnr, reconframe], feed_dict={
                inputImage: image1,
                previousImage: image2
            })

    if not os.path.exists(features_folder):
        os.mkdir(features_folder)

    with open(features_folder + 'quantized_res_feature.pkl', 'wb') as file:
        joblib.dump(Res_q, file)

    with open(features_folder + 'quantized_res_prior_feature.pkl', 'wb') as file:
        joblib.dump(Res_prior_q, file)

    with open(features_folder + 'quantized_motion_feature.pkl', 'wb') as file:
        joblib.dump(motion_q, file)

def decoder(image2, features_folder, decoder_model_path):
    """
    Function to decode encoded features into video frame.

    Parameters
    ----------
        image2: numpy.ndarray
            image in the form of numpy array
        features_folder: string
            folder from which encoded features are read

    Returns
    ----------
        recon_frame: numpy.ndarray
            reconstructed image in the form of numpy array
    """
    graph = load_graph(decoder_model_path)

    reconframe = graph.get_tensor_by_name('import/build_towers/tower_0/train_net_inference_one_pass/train_net/ReconFrame:0')
    res_input = graph.get_tensor_by_name('import/quant_feature:0')
    res_prior_input = graph.get_tensor_by_name('import/quant_z:0')
    motion_input = graph.get_tensor_by_name('import/quant_mv:0')
    previousImage = graph.get_tensor_by_name('import/input_image_ref:0')

    with tf.compat.v1.Session(graph=graph) as sess:

        with open(features_folder + 'quantized_res_feature.pkl', 'rb') as file:
            residual_feature = joblib.load(file)

        with open(features_folder + 'quantized_res_prior_feature.pkl', 'rb') as file:
            residual_prior_feature = joblib.load(file)

        with open(features_folder + 'quantized_motion_feature.pkl', 'rb') as file:
            motion_feature = joblib.load(file)

        dim = (1664, 896)
        image2 = cv2.resize(image2, dim, interpolation = cv2.INTER_LANCZOS4)
        image2 = image2 / 255.0
        image2 = np.expand_dims(image2, axis=0)

        # reconstructed image
        recon_d = sess.run(
            [reconframe],
            feed_dict={
                res_input: residual_feature,
                res_prior_input: residual_prior_feature,
                motion_input: motion_feature,
                previousImage: image2
            })

        recon_frame = np.squeeze(recon_d[0], axis=0)
        recon_frame = recon_frame * 255.0
        return recon_frame

def codec(video_list, encoder_model_path, decoder_model_path):
    """
    Neural network codec that combines encoder and decoder.

    Parameters
    ----------
        video_list: list
            list of input videos

    Returns
    ----------
        recon_frame: numpy.ndarray
            reconstructed image in the form of numpy array
    """
    features_folder = './features/'
    print("video_list", video_list)
    print(len(video_list))
    print(type(video_list[0]))


    for video in video_list:
        print(type(video))
        print(video)
        cap = cv2.VideoCapture(video.get_file().strip("'"))
        if not cap.isOpened():
            exit()

        # Keep the aspect ratio 13:7
        frame_width = 1664
        frame_height = 896
        fps = int(cap.get(5))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        print(video.get_title())
        print(type(video.get_title()))
        output_path = video.get_title().replace('.mp4', '_output.mp4')
        print("output_path", output_path)
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        i = 0
        image2 = np.empty([frame_width, frame_height])
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if i != 0:
                encoder(image1 = frame, image2 = image2, features_folder = features_folder, encoder_model_path = encoder_model_path)
                reconstructed_frame = decoder(image2, features_folder = features_folder, decoder_model_path = decoder_model_path)
                cv2.imwrite('temp.jpg', reconstructed_frame)
                print("reconstructed frame type", type(reconstructed_frame))
                out.write(cv2.imread('temp.jpg', cv2.IMREAD_UNCHANGED))

            image2 = frame
            i += 1

        cap.release()
        out.release()

        # ffmpeg encoding to contain file size
        name = Path(str(output_path)).stem
        output_folder = output_path.split("/")[0]
        encoded_video_name = os.path.join(output_folder, name + "_ffmpeg.mp4")
        cmd = f"static_ffmpeg -y -i {output_path} -c:v libx264 -crf 34 -preset veryfast {encoded_video_name}"
        subprocess.run(cmd, shell=True)

def main():
    """
    Runner method for neural network based codec. This method abstracts some of the interaction with S3 and AWS away from nn_codec.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path
    """
    config = ConfigHandler("reduction.nn_codec")
    s3_args = config.s3
    method_args = config.method
    download_model(s3_args, method_args)
    cloud_functionality = CloudFunctionality()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)

    codec(video_list, method_args['encoder_model_path'], method_args['decoder_model_path'])

    cloud_functionality.postprocess_reduction(s3_args, method_args)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

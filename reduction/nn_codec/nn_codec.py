"""Module to reduce video using neural network codec."""
import os
import sys
import cv2
import numpy as np
import tensorflow as tf
from joblib import dump, load
from boto3 import client
from time import time
from subprocess import run
from pathlib import Path
from aEye import Aux

root_path = run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality

def download_models(s3_args, method_args):
    """
    Downloads encoder and decoder model files from s3 to a local path.

    Parameters
    ----------
    s3_args: dict
        Defines the s3 bucket params
    method_args: dict
        Defines reduction technique specific args
    """
    s3 = client("s3")
    with open(method_args['encoder_model_path'], "wb") as file:
        s3.download_fileobj(s3_args['model_bucket_s3'],method_args['encoder_model_prefix_s3'],file)

    with open(method_args['decoder_model_path'], "wb") as file:
        s3.download_fileobj(s3_args['model_bucket_s3'],method_args['decoder_model_prefix_s3'],file)

def delete_models(method_args):
    """
    Deletes encoder and decoder model files from local.

    Parameters
    ----------
    s3_args: dict
        Defines the s3 bucket params
    method_args: dict
        Defines reduction technique specific args
    """
    os.remove(method_args['encoder_model_path'])
    os.remove(method_args['decoder_model_path'])

def load_graph(frozen_graph_filename):
    """
    Loads tensorflow model graph from a file.

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

def encoder(image1, image2, features_folder, encoder_model_path, width, height):
    """
    Encodes video frames into features and saves these features into pickle files.

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
    res = graph.get_tensor_by_name(prefix + 'Residual_Feature:0')
    input_image = graph.get_tensor_by_name('import/input_image:0')
    previous_image = graph.get_tensor_by_name('import/input_image_ref:0')
    res_prior = graph.get_tensor_by_name(prefix + 'Residual_Prior_Feature:0')
    motion = graph.get_tensor_by_name(prefix + 'Motion_Feature:0')
    bpp = graph.get_tensor_by_name(prefix + 'rate/Estimated_Bpp:0')
    psnr = graph.get_tensor_by_name(prefix + 'distortion/PSNR:0')
    reconframe = graph.get_tensor_by_name(prefix + 'ReconFrame:0')

    with tf.compat.v1.Session(graph=graph) as sess:
        image1 = cv2.resize(image1, (width, height), interpolation = cv2.INTER_LANCZOS4)
        image2 = cv2.resize(image2, (width, height), interpolation = cv2.INTER_LANCZOS4)
        image1 = image1 / 255.0
        image2 = image2 / 255.0
        image1 = np.expand_dims(image1, axis=0)
        image2 = np.expand_dims(image2, axis=0)

        bpp_est, res_q, res_prior_q, motion_q, psnr_val, recon_val = sess.run(
            [bpp, res, res_prior, motion, psnr, reconframe], feed_dict={
                input_image: image1,
                previous_image: image2
            })

    if not os.path.exists(features_folder):
        os.mkdir(features_folder)

    with open(features_folder + 'quantized_res_feature.pkl', 'wb') as file:
        dump(res_q, file)

    with open(features_folder + 'quantized_res_prior_feature.pkl', 'wb') as file:
        dump(res_prior_q, file)

    with open(features_folder + 'quantized_motion_feature.pkl', 'wb') as file:
        dump(motion_q, file)

def decoder(image2, features_folder, decoder_model_path, width, height):
    """
    Decodes encoded features from pickle files into video frame.

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

    reconframe = graph.get_tensor_by_name\
        ('import/build_towers/tower_0/train_net_inference_one_pass/train_net/ReconFrame:0')
    res_input = graph.get_tensor_by_name('import/quant_feature:0')
    res_prior_input = graph.get_tensor_by_name('import/quant_z:0')
    motion_input = graph.get_tensor_by_name('import/quant_mv:0')
    previous_image = graph.get_tensor_by_name('import/input_image_ref:0')

    with tf.compat.v1.Session(graph=graph) as sess:

        with open(features_folder + 'quantized_res_feature.pkl', 'rb') as file:
            residual_feature = load(file)

        with open(features_folder + 'quantized_res_prior_feature.pkl', 'rb') as file:
            residual_prior_feature = load(file)

        with open(features_folder + 'quantized_motion_feature.pkl', 'rb') as file:
            motion_feature = load(file)

        image2 = cv2.resize(image2, (width, height), interpolation = cv2.INTER_LANCZOS4)
        image2 = image2 / 255.0
        image2 = np.expand_dims(image2, axis=0)

        # reconstructed image
        recon_d = sess.run(
            [reconframe],
            feed_dict={
                res_input: residual_feature,
                res_prior_input: residual_prior_feature,
                motion_input: motion_feature,
                previous_image: image2
            })

        recon_frame = np.squeeze(recon_d[0], axis=0)
        recon_frame = recon_frame * 255.0
        return recon_frame

def codec(video_list, encoder_model_path, decoder_model_path, width, height, path = "temp"):
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
    print("width", type(width))
    print("height", type(height))

    for video in video_list:
        cap = cv2.VideoCapture(video.get_file().strip("'"))
        video_name = Path(str(video)).stem
        if not cap.isOpened():
            exit()

        fps = int(cap.get(5))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_filename = os.path.join(path, video_name + "_output.mp4")
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
        i = 0
        image2 = np.empty([width, height])
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if i != 0:
                encoder(image1 = frame, image2 = image2, features_folder = features_folder,
                        encoder_model_path = encoder_model_path, width = width, height = height)
                reconstructed_frame = decoder(image2, features_folder = features_folder,
                                              decoder_model_path = decoder_model_path,
                                              width = width, height = height)
                cv2.imwrite('temp.jpg', reconstructed_frame)
                out.write(cv2.imread('temp.jpg', cv2.IMREAD_UNCHANGED))

            image2 = frame
            i += 1

        cap.release()
        out.release()

        encoded_video_name = os.path.join(path, video_name)
        cmd = f"static_ffmpeg -y -i {output_filename} -c:v libx264 -crf 34 " + \
                f"-preset veryfast {encoded_video_name}.mp4"
        run(cmd, shell=True)
        os.remove(output_filename)
        os.remove("temp.jpg")

def main():
    """
    Runner method for neural network based codec. This method abstracts
    some of the interaction with S3 and AWS away from nn_codec.

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
    download_models(s3_args, method_args)
    cloud_functionality = CloudFunctionality()
    aux = Aux()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)

    codec(video_list, method_args['encoder_model_path'], method_args['decoder_model_path'],
          int(method_args['width']), int(method_args['height']), method_args["temp_path"])

    cloud_functionality.postprocess_reduction(s3_args, method_args)

    delete_models(method_args)

    aux.set_local_path("./features")
    aux.clean()

if __name__ == "__main__":
    start_time = time()
    main()
    print(f"--- {(time() - start_time)} seconds ---")

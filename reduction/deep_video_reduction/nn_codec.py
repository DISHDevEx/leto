import os
import subprocess
import joblib
import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path


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
    with tf.io.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)
    return graph

def encoder(image1, image2):
    """
    Function to encode video frames into features and save these features into pickle files.

    Parameters
    ----------
        image1: numpy.ndarray
            Image in the form of numpy array.
        image2: numpy.ndarray
            Image in the form of numpy array.
    """
    graph = load_graph('./model/L256/frozen_model_E.pb')
    outputfolder = './testpkl/'
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

    if not os.path.exists(outputfolder):
        os.mkdir(outputfolder)

    with open(outputfolder + 'quantized_res_feature.pkl', 'wb') as f:
        joblib.dump(Res_q, f)

    with open(outputfolder + 'quantized_res_prior_feature.pkl', 'wb') as f:
        joblib.dump(Res_prior_q, f)

    with open(outputfolder + 'quantized_motion_feature.pkl', 'wb') as f:
        joblib.dump(motion_q, f)

def decoder(image2):
    """
    Function to decode encoded features into video frame.

    Parameters
    ----------
        image2: numpy.ndarray
            image in the form of numpy array

    Returns
    ----------
        recon_frame: numpy.ndarray
            reconstructed image in the form of numpy array
    """
    graph = load_graph('./model/L256/frozen_model_D.pb')
    outputfolder = './testpkl/'
    reconframe = graph.get_tensor_by_name('import/build_towers/tower_0/train_net_inference_one_pass/train_net/ReconFrame:0')
    res_input = graph.get_tensor_by_name('import/quant_feature:0')
    res_prior_input = graph.get_tensor_by_name('import/quant_z:0')
    motion_input = graph.get_tensor_by_name('import/quant_mv:0')
    previousImage = graph.get_tensor_by_name('import/input_image_ref:0')

    with tf.compat.v1.Session(graph=graph) as sess:

        with open(outputfolder + 'quantized_res_feature.pkl', 'rb') as f:
            residual_feature = joblib.load(f)

        with open(outputfolder + 'quantized_res_prior_feature.pkl', 'rb') as f:
            residual_prior_feature = joblib.load(f)

        with open(outputfolder + 'quantized_motion_feature.pkl', 'rb') as f:
            motion_feature = joblib.load(f)

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

def codec(video_path):
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
    cap = cv2.VideoCapture(video_path)

    # Keep the aspect ratio 13:7
    frame_width = 1664
    frame_height = 896
    fps = int(cap.get(5))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_path = video_path.replace('.mp4', '_output.mp4')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    i = 0
    image2 = np.empty([frame_width, frame_height])
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if i != 0:
            encoder(image1 = frame, image2 = image2)
            reconstructed_frame = decoder(image2)
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

if __name__ == '__main__':
    codec('./licenseplate04.mp4')

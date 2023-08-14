"""
Module that enhances video resolution using pretained models: edsr_x4,espcn_x4,fsrcnn_x4,lapsrn_x4.
"""
import os
import sys
import cv2
import subprocess
from cv2 import dnn_superres
from aEye import Aux
import logging 
import configparser

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")
# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality


def create_model_name(model_prefix_s3):
    """
    Method that super resolves videos using pretrained using pretained models: edsr_x4,espcn_x4,fsrcnn_x4,lapsrn_x4.

    Parameters
    ----------
        model_prefix_s3: string
            the prefix of the pretrained model as stored in s3.

    Returns
    ----------
        split_on_scaling: string
            defines which model to use for cv2.dnn_superres as parsed from the model_prefix_s3
    """

    split_on_file_name = model_prefix_s3.split("/")
    split_on_file_extension = split_on_file_name[1].split(".")
    split_on_scaling = split_on_file_extension[0].split("_")
    return split_on_scaling[0]


def superres_video(method_args, s3_args):
    """
    Method that super resolves videos using pretrained using pretained models: edsr_x4,espcn_x4,fsrcnn_x4,lapsrn_x4.

    Parameters
    ----------
        method_args:
            configparser object.  Parameters defined in ~/config.ini

    """

    for i in range(len(os.listdir("reduced_videos"))):
        input_video_path = os.path.join(
            "./reduced_videos/", os.listdir("reduced_videos")[i]
        )
        superres_video_path = os.path.join(
            "./reconstructed_videos/", os.listdir("reduced_videos")[i]
        )
        input_video = cv2.VideoCapture(input_video_path)
        fourcc = cv2.VideoWriter_fourcc(*method_args['codec'])

        height = method_args.getint('height')
        width = method_args.getint('width')
        resolution = (width, height)

        fps = input_video.get(cv2.CAP_PROP_FPS)
        superres_video = cv2.VideoWriter(
            superres_video_path, fourcc, fps, resolution
        )

        # Create an instance of DNN Super Resolution implementation class
        model = dnn_superres.DnnSuperResImpl_create()
        model.readModel(method_args['local_model_path'])

        model.setModel(create_model_name(method_args['model_prefix_s3']), 4)

        while input_video.isOpened():
            ret, frame = input_video.read()
            if not ret:
                break

            result = model.upsample(frame)

            # Resize frame
            resized = cv2.resize(
                result, resolution, interpolation=cv2.INTER_LANCZOS4
            )

            # Write resized frame to the output video file
            superres_video.write(resized)

        # Release video capture and writer objects
        input_video.release()
        superres_video.release()


if __name__ == "__main__":
    cloud_functionality = CloudFunctionality()

    # load and allocate config file
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    config.read('../../config.ini')
    s3_args = config['DEFAULT']
    method_args = config['reconstruction.recon_args']
    logging.info("successfully loaded config file")

    cloud_functionality.preprocess(method_args, s3_args)

    superres_video(method_args, s3_args)

    cloud_functionality.postprocess(method_args, s3_args)

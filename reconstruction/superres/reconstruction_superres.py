"""
Module that enhances video resolution using Deep Neural Networks.
"""
import os
import sys
import cv2
import boto3
import argparse
import subprocess
from cv2 import dnn_superres
from aEye import Aux

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")
# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality
from utilities import parse_recon_args


def create_model_name(model_prefix_s3):
    split_on_file_name = model_prefix_s3.split("/")
    split_on_file_extension = split_on_file_name[1].split(".")
    split_on_scaling = split_on_file_extension[0].split("_")
    return split_on_scaling[0]


def superres_video(args):
    """
    Function that enhances video resolution using Deep Neural Networks.
    """

    for i in range(len(os.listdir("reduced_videos"))):
        input_video_path = os.path.join(
            "./reduced_videos/", os.listdir("reduced_videos")[i]
        )
        superres_video_path = os.path.join(
            "./reconstructed_videos/", os.listdir("reduced_videos")[i]
        )
        input_video = cv2.VideoCapture(input_video_path)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = input_video.get(cv2.CAP_PROP_FPS)
        superres_video = cv2.VideoWriter(
            superres_video_path, fourcc, fps, args.resolution
        )

        # Create an instance of DNN Super Resolution implementation class
        model = dnn_superres.DnnSuperResImpl_create()
        model.readModel(args.local_model_path)

        model.setModel(create_model_name(args.model_prefix_s3), 4)

        while input_video.isOpened():
            ret, frame = input_video.read()
            if not ret:
                break

            result = model.upsample(frame)

            # Resize frame
            resized = cv2.resize(
                result, args.resolution, interpolation=cv2.INTER_LANCZOS4
            )

            # Write resized frame to the output video file
            superres_video.write(resized)

        # Release video capture and writer objects
        input_video.release()
        superres_video.release()


if __name__ == "__main__":
    cloud_functionality = CloudFunctionality()

    args = parse_recon_args()

    cloud_functionality.preprocess(args)

    superres_video(args)

    cloud_functionality.postprocess(args)
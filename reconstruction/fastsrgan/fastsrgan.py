"""
Module that enhances video resolution using the pretrained FastSRGAN.
"""
import os
import sys
import cv2
import subprocess
import tensorflow as tf
from tensorflow import keras
import numpy as np
import configparser
import logging


# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality


def super_resolve_video(method_args):
    """
    Super resolve's videos using a pretained "FastSRGAN".

    Parameters
    ----------
        method_args:
            configparser object.  Parameters defined in ~/config.ini
            
    """
    # Loop through all videos that need to be reduced.
    for i in range(len(os.listdir("reduced_videos"))):
        input_video_path = os.path.join(
            "./reduced_videos/", os.listdir("reduced_videos")[i]
        )

        superres_video_path = os.path.join(
            "./reconstructed_videos/", os.listdir("reduced_videos")[i]
        )

        input_video = cv2.VideoCapture(input_video_path)

        # Create a variable to store the choice codec for the output video.
        fourcc = cv2.VideoWriter_fourcc(*method_args['codec'])

        fps = input_video.get(cv2.CAP_PROP_FPS)

        superres_video = cv2.VideoWriter(superres_video_path, fourcc, fps, (1440, 1920))

        # Create an instance of fastsrgan model
        model = keras.models.load_model("fastsrgan.h5")

        while input_video.isOpened():
            ret, frame = input_video.read()
            if ret is True:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Rescale to 0-1.
                frame = frame / 255.0

                sr_frame = model.predict(np.expand_dims(frame, axis=0))[0]

                sr_frame = (((sr_frame + 1) / 2.0) * 255).astype(np.uint8)

                sr_frame = cv2.cvtColor(sr_frame, cv2.COLOR_RGB2BGR)

                superres_video.write(sr_frame)
            else:
                break

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

    super_resolve_video(method_args)

    cloud_functionality.postprocess(method_args, s3_args)

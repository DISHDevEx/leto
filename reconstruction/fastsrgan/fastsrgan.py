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


# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionalityReconstruction
from utilities import ConfigHandler


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

        resized_width = int(4 * input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        resized_height = int(4 * input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        superres_video = cv2.VideoWriter(superres_video_path, fourcc, fps, (resized_width,resized_height))

        # Create an instance of fastsrgan model
        model = keras.models.load_model(method_args['local_model_path'])

        while input_video.isOpened():
            ret, frame = input_video.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Rescale to 0-1.
            frame = frame / 255.0

            sr_frame = model.predict(np.expand_dims(frame, axis=0))[0]

            sr_frame = (((sr_frame + 1) / 2.0) * 255).astype(np.uint8)

            sr_frame = cv2.cvtColor(sr_frame, cv2.COLOR_RGB2BGR)

            sr_frame = cv2.resize(sr_frame, (resized_width,resized_height))

            superres_video.write(sr_frame)

        # Release video capture and writer objects
        input_video.release()
        superres_video.release()


if __name__ == "__main__":
    # load and allocate config file
    config = ConfigHandler('reconstruction.fastsrgan')
    s3_args = config.s3
    method_args = config.method

    with CloudFunctionalityReconstruction(s3_args, method_args) as cloud_functionality:

        cloud_functionality.preprocess_reconstruction(s3_args,method_args)

        cloud_functionality.download_model(s3_args, method_args)
        
        super_resolve_video(method_args)

        cloud_functionality.upload_reconstruction(s3_args,method_args)
        
"""
Module that upscales video using openCV.
"""
import subprocess
import argparse
import cv2
import os
import sys
from aEye import Aux

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality
from utilities import ConfigHandler


def upscale_video(method_args):
    """
    Method that upscales video using opencv and merges audio with the upscaled video.

    Parameters
    ----------
        method_args:
            configparser object.  Parameters defined in ~/config.ini
       
    """

    for i in range(len(os.listdir("reduced_videos"))):
        input_video_path = os.path.join(
            "./reduced_videos/", os.listdir("reduced_videos")[i]
        )
        upscaled_video_path = os.path.join(
            "./reconstructed_videos/", os.listdir("reduced_videos")[i]
        )
        input_video = cv2.VideoCapture(input_video_path)
        fps = input_video.get(cv2.CAP_PROP_FPS)
        codec = cv2.VideoWriter_fourcc(*method_args['codec'])
        height = method_args.getint('height')
        width = method_args.getint('width')
        resolution = (width, height)

        upscaled_video = cv2.VideoWriter(
            upscaled_video_path, codec, fps, resolution
        )
        while input_video.isOpened():
            ret, frame = input_video.read()
            if ret is True:
                resized_frame = cv2.resize(
                    frame, resolution, fx=0, fy=0, interpolation=cv2.INTER_LANCZOS4
                )
                upscaled_video.write(resized_frame)
            else:
                break
        P = subprocess.Popen(
            [
                "static_ffmpeg",
                "-show_streams",
                "-print_format",
                "json",
                input_video_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        streams = P.communicate()[0]
        streams = streams.decode("utf-8")
        if "audio" in streams.lower():
            # Extract audio from source video
            subprocess.call(
                ["static_ffmpeg", "-i", input_video_path, "sourceaudio.mp3"], shell=True
            )
            # Merge source audio and upscaled video
            subprocess.call(
                [
                    "static_ffmpeg",
                    "-i",
                    upscaled_video_path,
                    "-i",
                    "sourceaudio.mp3",
                    "-map",
                    "0:0",
                    "-map",
                    "1:0",
                    upscaled_video_path,
                ],
                shell=True,
            )
        else:
            pass

        # Release the video capture and writer objects
        input_video.release()
        upscaled_video.release()


if __name__ == "__main__":
    cloud_functionality = CloudFunctionality()

    config = ConfigHandler('reconstruction.opencv_ru')
    s3_args = config.s3
    method_args = config.method

    cloud_functionality.preprocess(method_args, s3_args)

    upscale_video(method_args)

    cloud_functionality.postprocess(method_args, s3_args)

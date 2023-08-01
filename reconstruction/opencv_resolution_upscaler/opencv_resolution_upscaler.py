"""
Module that upscales video using openCV.
"""
import subprocess
import argparse
import cv2
import os
import boto3
import static_ffmpeg
import sys
from aEye import Aux

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality
from utilities import parse_recon_args


def upscale_video(args):
    """
    Method that upscales video using opencv and merges audio with the upscaled video.
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
        codec = cv2.VideoWriter_fourcc(*"mp4v")

        upscaled_video = cv2.VideoWriter(
            upscaled_video_path, codec, fps, tuple(args.resolution)
        )
        while input_video.isOpened():
            ret, frame = input_video.read()
            if ret is True:
                resized_frame = cv2.resize(
                    frame, args.resolution, fx=0, fy=0, interpolation=cv2.INTER_LANCZOS4
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

    args = parse_recon_args()

    cloud_functionality.preprocess(args)

    upscale_video(args)

    cloud_functionality.postprocess(args)

"""
Script to change the fps and bitrate of a video via ffmpeg.
"""

from pathlib import Path
import subprocess
from aEye import Labeler
from aEye import Aux
import sys
import logging
import math

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality


def fps_bitrate(video_list, fps_factor=2, bitrate_factor=2):
    """
    Wrapper method for the change_fps and set_bitrate methods in aEye.Labeler.

    This method adds labels to the input videos for fps and file bitrate reduction.
    The labels are then executed in the runner method to process the videos.
    Default settings of fps=30 and bitrate=0 result in the output videos having
    30 frames per second and a 10x reduction from original file bitrate.

    Parameters
    ----------
        video_list: list
            list of input videos

        fps_factor: int
            Desired X factor reduction for frames per second.

        bitrate_factor: int
            Desired X factor reduction for video internal bitrate.


    Returns
    ----------
        video_list: list
            list of videos with changes labeled for bitrate and framerate reduction; to be processed in runner method
    """

    labeler = Labeler()

    modified_video_list = []

    for video in video_list:
        video.extract_metadata()

        video_current_fps = int(
            video.meta_data["streams"][0]["avg_frame_rate"].split("/")[0]
        )

        video_current_bitrate = int(video.meta_data["streams"][0]["bit_rate"])

        requested_fps = video_current_fps / fps_factor

        requested_bitrate = math.ceil(video_current_bitrate / (bitrate_factor * 1000))

        labeler.change_fps([video], requested_fps)

        labeler.set_bitrate([video], requested_bitrate)

    return modified_video_list


def main():
    """
    Runner method for fps_bitrate.fps_bitrate().  This method abstracts some of the
    interaction with S3 and AWS away from fps_bitrate.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.
    """
    config = ConfigHandler("reduction.fps_bitrate")
    s3_args = config.s3
    method_args = config.method
    aux = Aux()
    cloud_functionality = CloudFunctionality()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)
    fps_bitrate(
        video_list,
        method_args.getint("fps_factor"),
        method_args.getint("bitrate_factor"),
    )
    aux.execute_label_and_write_local(video_list, path=method_args["temp_path"])
    cloud_functionality.postprocess_reduction(s3_args, method_args)

    return logging.info("video reduction completed on " + sys.version + ".")


if __name__ == "__main__":
    main()

"""
Script to change the fps and bitrate of a video via ffmpeg.
"""

from pathlib import Path
import subprocess
from aEye import Labeler
from aEye import Aux
import sys
import logging

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality


def fps_bitrate(video_list, fps=30, bitrate=0):
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

        fps: int | default --> 30
            desired Frames per Second (fps) for output videos to be clocked to

        bitrate: int | default --> 0
            desired bitrate for the videos. This is given in Kb, so setting it to 1.5 Mb for example should be
            1500, not 1.5.

            Default Setting: Setting to 0 will do a 10x bitrate reduction

    Returns
    ----------
        video_list: list
            list of videos with changes labeled for bitrate and framerate reduction; to be processed in runner method
    """

    labeler = Labeler()

    try:
        if fps < 1:
            raise Exception
        labeler.change_fps(video_list, fps)
    except Exception:
        logging.exception("unable to process with given fps; must be > 0")

    try:
        if bitrate < 0:
            raise Exception

        labeler.set_bitrate(video_list, bitrate)
    except Exception:
        logging.exception("unable to process with given bitrate; must be >= 0")

    return video_list


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
    config = ConfigHandler('reduction.fps_bitrate')
    s3_args = config.s3
    method_args = config.method
    aux = Aux()
    cloud_functionality = CloudFunctionality()
    
    
    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args )
    fps_bitrate(video_list, method_args.getint('fps'), method_args.getint('bitrate'))
    aux.execute_label_and_write_local(video_list,path=method_args['temp_path'])
    cloud_functionality.postprocess_reduction(s3_args, method_args)

    return logging.info("video reduction completed on " + sys.version + ".")


if __name__ == "__main__":
    main()

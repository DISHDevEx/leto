"""
Script to change the resolution of a video via ffmpeg.
"""

import logging
import subprocess
import sys

from aEye import Labeler
from aEye import Aux

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler



def main():
    """
    Runner method for ffmpeg resolution downsampler.  This method abstracts some of the
    interaction with S3 and AWS away from ffmpeg.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.
    """

    logging.info("running reduction module")

    config = ConfigHandler('reduction.ffmpeg_resolution_downsampler')
    s3 = config.s3
    method = config.method

    aux = Aux()

    labeler = Labeler()

    video_list_s3 = aux.load_s3(
        bucket = s3['input_bucket_s3'], prefix= method['input_prefix_s3']
    )

    downsampled_video = labeler.change_resolution(
        video_list_s3, method['quality'], method['algorithm']
    )

    aux.execute_label_and_write_local(downsampled_video)

    aux.upload_s3(
        downsampled_video, bucket=method['output_bucket_s3'], prefix= method['output_prefix_s3']
    )

    aux.clean()


if __name__ == "__main__":
    main()

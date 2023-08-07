"""
Script to change the resolution of a video via ffmpeg.
"""

import argparse
import logging

from aEye import Video
from aEye import Labeler
from aEye import Aux

import os


def parse_args():
    """
    Parses the arguments needed for ffmpeg based reduction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix, quality{eg. 360p}, algorithm{eg. lanczos, bicubic }.


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix, quality{eg. 360p}, algorithm{eg. lanczos, bicubic }.
    """

    parser = argparse.ArgumentParser(
        description="Inference script of ffmpeg resolution downsampler"
    )
    parser.add_argument(
        "--input_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the input video",
    )

    parser.add_argument(
        "--input_prefix_s3",
        type=str,
        default="original-videos/benchmark/car/",
        help="s3 prefix of the input video",
    )

    parser.add_argument(
        "--output_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the input video",
    )

    parser.add_argument(
        "--output_prefix_s3",
        type=str,
        default="reduced-videos/benchmark/ffmpeg-360/car/",
        help="s3 prefix of the output video",
    )

    parser.add_argument(
        "--quality",
        type=str,
        default="360p",
        help="Can use: 240p, 360p,480p,720p,1080p as inputs.",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="lanczos",
        help="Refer https://ffmpeg.org/ffmpeg-scaler.html to see the ffmpeg scaler algorithms.",
    )

    args = parser.parse_args()

    return args


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

    args = parse_args()

    aux = Aux()

    labeler = Labeler()

    video_list_s3 = aux.load_s3(
        bucket=args.input_bucket_s3, prefix=args.input_prefix_s3
    )

    downsampled_video = labeler.change_resolution(video_list_s3, args.quality, args.algorithm)

    aux.execute_label_and_write_local(downsampled_video)

    aux.upload_s3(
        downsampled_video, bucket=args.output_bucket_s3, prefix=args.output_prefix_s3
    )

    aux.clean()


if __name__ == "__main__":
    main()

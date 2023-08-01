import argparse
import logging

from aEye import Video
from aEye import Labeler
from aEye import Aux

import os


def parse_args():
    """
    Parses the arguments needed for RealBasicVSR reconstruction module.
    Catalogues: config, checkpoint, input dir, output dir, maximum sequence length, and fps


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent config, checkpoint, input dir, output dir, maximum sequence length, and fps.
    """

    parser = argparse.ArgumentParser(
        description="PostProcessing script for RealBasicVSR in Leto"
    )
    parser.add_argument(
        "--output_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the input video",
    )

    parser.add_argument(
        "--ouput_prefix_s3",
        type=str,
        default="reconstructed-videos/benchmark/realbasicvsr/car/",
        help="s3 prefix of the input video",
    )

    parser.add_argument(
        "--clean_model",
        type=str,
        default="True",
        help="String to indicate to clean video or not  input video",
    )

    args = parser.parse_args()

    return args


def main():
    logging.info("running postprocessing for RealBasicVSR")

    args = parse_args()

    aux = Aux()

    recon_vid_obj = aux.load_local("./reconstructed_videos")

    aux.set_local_path("./reconstructed_videos")

    aux.upload_s3(
        recon_vid_obj, bucket=args.output_bucket_s3, prefix=args.ouput_prefix_s3
    )

    aux.clean()

    aux.set_local_path("./reduced_videos/")

    aux.clean()

    # After cleaning videos, delete the pretrained model as well.
    if args.clean_model.lower() == "true":
        os.remove("./realbasicvsr_x4.pth")


if __name__ == "__main__":
    main()

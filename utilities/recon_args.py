import argparse


def parse_recon_args():
    """
    Parses the arguments needed for reconstruction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
            codec, resolution, model bucket, model prefix and algorithm.

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix, codec, resolution, model bucket, model prefix and algorithm.
    """

    parser = argparse.ArgumentParser(description="Inference script of upscaler")

    parser.add_argument(
        "--input_bucket_s3",
        type=str,
        help="s3 bucket of the input video",
        default="leto-dish",
    )

    parser.add_argument(
        "--input_prefix_s3",
        type=str,
        help="s3 prefix of the input video",
        default="reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/",
    )

    parser.add_argument(
        "--output_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the output video",
    )

    parser.add_argument(
        "--output_prefix_s3",
        type=str,
        default="reconstructed-videos/benchmark/misc/car/",
        help="s3 prefix of the output video",
    )

    parser.add_argument(
        "--download_model",
        type=str,
        default="True",
        help="string boolean to indicate if a model needs to be downloaded",
    )

    parser.add_argument(
        "--model_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the pre-trained model",
    )

    parser.add_argument(
        "--model_prefix_s3",
        type=str,
        default="pretrained-models/fastsrgan.h5",
        help="s3 prefix of the pre-trained model",
    )

    parser.add_argument(
        "--local_model_path",
        type=str,
        default="fastsrgan.h5",
        help="local path to save pre-trained model",
    )

    parser.add_argument(
        "--clean_model",
        type=str,
        default="True",
        help="String to indicate to clean video or not  input video",
    )

    parser.add_argument("--codec", type=str, default="mp4v", help="video codec")

    parser.add_argument(
        "--resolution",
        type=int,
        nargs="+",
        default=[1920, 1080],
        help="desired video resolution",
    )

    args = parser.parse_args()

    return args

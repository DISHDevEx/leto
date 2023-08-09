import ffmpeg
import subprocess

from aEye import Video
from aEye import Labeler
from aEye import Aux
import sys
import logging
import argparse
import os


def parse_args():
    """
    Parses the arguments needed for Super Resolution reconstruction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
            quality, crf, and temp path.

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix, quality, crf, and temp path.
    """

    parser = argparse.ArgumentParser(description="A script of opencv jpg reduction")

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
        default="original-videos/benchmark/car/",
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
        default="reduced-videos/benchmark/cv2_reduction/car/",
        help="s3 prefix of the output video",
    )

    parser.add_argument(
        "--temp_path",
        type=str,
        default="temp",
        help="A temp folder to store video from uploading to s3",
    )

    args = parser.parse_args()

    return args

def video_to_gif(input_video_path, output_path):

# Replace these with your actual input and output file paths
    input_video_path = input_video_path
    output_gif_path = output_path
    # Run the ffmpeg command to convert video to GIF
    command = [
        "static_ffmpeg",
        "-i", input_video_path,
        "-vf", "fps=10,scale=640:-1:flags=lanczos",
        "-c:v", "gif",
        output_gif_path
    ]

    # Run the command
    subprocess.run(command)
    return print("File converted to gif")


def main():
    args = parse_args()
    aux = Aux()
    video_list_s3_original_video = aux.load_s3(
        bucket=args.input_bucket_s3 , prefix=args.input_prefix_s3e
    )
    
    if not os.path.exists("original_videos"):
        os.mkdir("./original_videos")
    
    aux.execute_label_and_write_local(video_list_s3_original_video, "original_videos")

    if not os.path.exists("gif_folder"):
        os.mkdir("./gif_folder")
    
    for file in os.listdir('original_videos'):
        video_to_gif(file, 'gif_folder')
    
    ## upload to s3 
    



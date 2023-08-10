import ffmpeg
import subprocess
from aEye import Aux
import sys
import logging
import argparse
import os
from pathlib import Path
import time


def parse_args():
    """
    Parses the arguments needed for Video to Gif conversion.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
    

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix
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
    return print("Check gif directory for conversion")


def main():
    args = parse_args()
    aux = Aux()
    video_list_s3_original_video = aux.load_s3(
        bucket=args.input_bucket_s3 , prefix=args.input_prefix_s3
    )
    
    if not os.path.exists("original_videos"):
        os.mkdir("./original_videos")
    
    aux.execute_label_and_write_local(video_list_s3_original_video, "original_videos")

    if not os.path.exists("gif_folder"):
        os.mkdir("./gif_folder")
    
    for file in os.listdir('original_videos'):
        print(file)
        video_name  = Path(file).stem
        filepath = os.path.join('./original_videos', file)
        print(filepath)
        output_filename = video_name + '.gif'
        outfilepath = os.path.join('./gif_folder', output_filename)
        video_to_gif(filepath,outfilepath )
    out_video_list = os.listdir('gif_folder')
    aux.upload_s3(out_video_list, bucket = args.output_bucket_s3, prefix = args.output_prefix_s3)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
    



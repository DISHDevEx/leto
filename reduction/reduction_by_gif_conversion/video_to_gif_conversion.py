import ffmpeg
import subprocess

from aEye import Video
from aEye import Labeler
from aEye import Aux
import sys
import logging
import argparse


# Replace these with your actual input and output file paths
input_video_path = "/Users/tamanna.kawatra/Desktop/video_streaming_analytics/Video_Benchmark_car.mp4"
output_gif_path = "car_output_30fps_640p.gif"

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

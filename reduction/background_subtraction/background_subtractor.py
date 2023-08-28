import cv2
from aEye import Aux
import logging
import os
from pathlib import Path

import subprocess
import time
import sys
import numpy as np

root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality


def background_subtractor(video_list, path="temp"):
    """ 
    This method helps to extract foreground from the video by removing static background
    Video works usually well on the videos with static background. 
    variables : fps(frame per second), num_frames(number of frames), width(frame width), 
    height(frame height) are used for frame manipulation
    
    Parameters:
    -------------
    video_list : list
    list of input videos 
    path: string
    path to local folder where reduced videos need to be stored

    Returns:
    ---------
    videos with background masked in S3 location
    
     """

    # Create the output folder if it doesn't exist
    # os.makedirs(output_folder, exist_ok=True)

    # Initialize video capture
    for video in video_list:
        stream = cv2.VideoCapture(video.get_file().strip("'"))
        if not stream.isOpened():
            exit()
        # Get the video's frame width, height, and frames per second
        video_name = Path(str(video)).stem
        fps = stream.get(cv2.CAP_PROP_FPS)
        width = int(stream.get(3))
        height = int(stream.get(4))
        output_filename = os.path.join(path, video_name + "_masked.mp4")
        output = cv2.VideoWriter(
            output_filename,
            cv2.VideoWriter_fourcc(*"mp4v"),  # Change FourCC code
            fps=fps,
            frameSize=(width, height),
            isColor=False,
        )  # Set isColor to False

        num_frames = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_ids = np.random.choice(num_frames, size=20, replace=False)
        frames = []
        # Looping through chosen frame ids
        for fid in frame_ids:
            stream.set(cv2.CAP_PROP_POS_FRAMES, fid)
            ret, frame = stream.read()
            if not ret:
                exit()
            frames.append(frame)

        median = np.median(frames, axis=0).astype(np.uint8)
        median_gray = cv2.cvtColor(median, cv2.COLOR_BGR2GRAY)

        stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # Looping through entire video
        while True:
            ret, frame = stream.read()
            if not ret:
                break

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff_frame = cv2.absdiff(median_gray, frame_gray)
            output.write(diff_frame)

            if cv2.waitKey(1) == ord("q"):
                break

        stream.release()
        output.release()
        cv2.destroyAllWindows()  # Release the VideoWriter
        median_frame_name = os.path.join(path, video_name + ".jpg")
        cv2.imwrite(median_frame_name, median)
        encoded_video_name = os.path.join(path, video_name)
        cmd = f"static_ffmpeg -y -i {output_filename} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}.mp4"
        subprocess.run(cmd, shell=True)
        os.remove(output_filename)


def main():
    """
    Runner method for background_subtractor().  This method abstracts some of the
    interaction with S3 and AWS away from fps_bitrate.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.'''
    
    """
    config = ConfigHandler("reduction.background_subtractor")
    s3_args = config.s3
    method_args = config.method
    aux = Aux()

    cloud_functionality = CloudFunctionality()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)

    background_subtractor(video_list, method_args["temp_path"])

    cloud_functionality.postprocess_reduction(s3_args, method_args)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

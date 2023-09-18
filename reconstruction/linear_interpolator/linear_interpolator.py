import cv2
import os
import subprocess
from pathlib import Path
import sys

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")
# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality
import time


def linear_interpolation(frame_a, frame_b, alpha):
    """
    Perform linear interpolation between two image frames.

    This function blends two input frames together using linear interpolation.
    The interpolation is controlled by the parameter 'alpha', where 0 <= alpha <= 1.
    When alpha is 0, the result will be identical to 'frame_a', and when alpha is 1,
    the result will be identical to 'frame_b'.

    Parameters:
     -----------
    - frame_a: The first input image frame (numpy.ndarray).
    - frame_b: The second input image frame (numpy.ndarray).
    - alpha: The interpolation parameter (float), where 0 <= alpha <= 1.
    
    Returns:
    ----------
    - interpolated_frame: The linearly interpolated image frame (numpy.ndarray)
    """
    return cv2.addWeighted(frame_a, 1 - alpha, frame_b, alpha, 0)


def reconstruct_video_with_keyframe_images(target_frame_rate=30):
    """
    Reconstruct a video with keyframe images.

    This function takes a set of video files from a directory of reduced videos and reconstructs
    them by interpolating frames to achieve a target frame rate. It saves the reconstructed video
    in the 'reconstructed_videos' directory.

    Parameters:
    ------------
    target_frame_rate: The desired frame rate for the reconstructed video (default is 30).

    Returns:
    ----------
    - None
    """
    path = "./reconstructed_videos"
    for video in os.listdir("./reduced_videos"):
        video_path = os.path.join("./reduced_videos", video)
        cap = cv2.VideoCapture(video_path)
        video_name = Path(str(video)).stem

        # Get video properties
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_size = (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        # calculate interpolated frames between two keyframes
        interpolation_factor = int((target_frame_rate / frame_rate) - 1)

        # Create VideoWriter to save interpolated video
        output_filename = os.path.join(path, video_name + "_interpolated.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for MP4 video
        out = cv2.VideoWriter(output_filename, fourcc, target_frame_rate, frame_size)

        # Read frames and perform interpolation
        ret, frame_a = cap.read()
        while ret:
            ret, frame_b = cap.read()

            if not ret:
                break

            # Perform linear interpolation
            for i in range(interpolation_factor + 1):
                alpha = i / (interpolation_factor + 1)
                interpolated_frame = linear_interpolation(frame_a, frame_b, alpha)
                out.write(interpolated_frame)

            frame_a = frame_b
        # writing last frame
        out.write(frame_b)

        # Release VideoCapture and VideoWriter
        cap.release()
        out.release()
        encoded_video_name = os.path.join(path, video_name)
        cmd = f"static_ffmpeg -y -i {output_filename} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}.mp4"
        subprocess.run(cmd, shell=True)
        os.remove(output_filename)


def main():
    """
    Runner method for linear interpolation().  This method abstracts some of the
    interaction with S3 and AWS away from fps_bitrate.

    Parameters:
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
        output video S3 path.
    """

    cloud_functionality = CloudFunctionality()

    # load and allocate config file
    config = ConfigHandler("reconstruction.linear_interpolator")
    s3_args = config.s3
    method_args = config.method

    cloud_functionality.preprocess_reconstruction(s3_args, method_args)

    reconstruct_video_with_keyframe_images(method_args.getint("target_frame_rate"))

    cloud_functionality.postprocess_reconstruction(s3_args, method_args)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

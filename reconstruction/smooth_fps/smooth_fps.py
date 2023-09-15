"""
This module contains functions for frame interpolation using neural networks.

Based on the research paper available at: https://arxiv.org/pdf/2204.03513.pdf
"""

import subprocess
import ffmpeg
import numpy
import torch
import sys
import model.m2m as m2m
import os

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionalityReconstruction
from utilities import ConfigHandler


def interpolate_frame(frame1, frame2):
    """
    Interpolate frames between frame1 and frame2 using the M2M model.

    Inputs:
    ----------
        frame1 (numpy.ndarray): The first frame.
        frame2 (numpy.ndarray): The second frame.

    Returns:
    ----------
        numpy.ndarray: The interpolated frame(s) between frame1 and frame2.
    """
    frame1_np = frame1[:, :, ::-1].astype(numpy.float32) * (1.0 / 255.0)
    frame2_np = frame2[:, :, ::-1].astype(numpy.float32) * (1.0 / 255.0)

    frame1_tensor = torch.FloatTensor(
        numpy.ascontiguousarray(frame1_np.transpose(2, 0, 1)[None, :, :, :])
    ).cuda()
    frame2_tensor = torch.FloatTensor(
        numpy.ascontiguousarray(frame2_np.transpose(2, 0, 1)[None, :, :, :])
    ).cuda()

    if int(method_args["factor"]) == 2:
        interpolated_frame_tensor = netNetwork(
            frame1_tensor,
            frame2_tensor,
            [torch.FloatTensor([0.5]).view(1, 1, 1, 1).cuda()],
        )[0]
        interpolated_frame_np = (
            (
                interpolated_frame_tensor.detach()
                .cpu()
                .numpy()[0, :, :, :]
                .transpose(1, 2, 0)[:, :, ::-1]
                * 255.0
            )
            .clip(0.0, 255.0)
            .round()
            .astype(numpy.uint8)
        )
        return interpolated_frame_np
    elif int(method_args["factor"]) > 2:
        interpolated_frames_tensor = [
            torch.FloatTensor([step / int(method_args["factor"])])
            .view(1, 1, 1, 1)
            .cuda()
            for step in range(1, int(method_args["factor"]))
        ]
        interpolated_frames = netNetwork(
            frame1_tensor,
            frame2_tensor,
            interpolated_frames_tensor,
            int(method_args["factor"]),
        )
        interpolated_frames_np = [
            (
                frame.detach().cpu().numpy()[0, :, :, :].transpose(1, 2, 0)[:, :, ::-1]
                * 255.0
            )
            .clip(0.0, 255.0)
            .round()
            .astype(numpy.uint8)
            for frame in interpolated_frames
        ]
        return interpolated_frames_np


def get_video_size(filename):
    """
    Get the width, height, and frames per second (fps) of a video file.

    Inputs:
    ----------
        filename (str): The path to the video file.

    Returns:
    ----------
        tuple: A tuple containing the width, height, and fps of the video.
    """
    probe = ffmpeg.probe(filename)
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    width = int(video_info["width"])
    height = int(video_info["height"])
    fps = int(video_info["avg_frame_rate"].split("/")[0])
    return width, height, fps


def start_ffmpeg_process_input(in_filename):
    """
    Start an FFmpeg process for input video.

    Inputs:
        in_filename (str): The input video file name.

    Returns:
        subprocess.Popen: A subprocess representing the FFmpeg process for input.
    """
    process_args = (
        ffmpeg.input(in_filename)
        .output("pipe:", format="rawvideo", pix_fmt="rgb24")
        .compile()
    )
    return subprocess.Popen(process_args, stdout=subprocess.PIPE)


def start_ffmpeg_process_output(out_filename, width, height, new_fps):
    """
    Start an FFmpeg process for output video.

    Inputs:
    ----------
        out_filename (str): The output video file name.
        width (int): The width of the video.
        height (int): The height of the video.
        new_fps (int): The new frames per second (fps) for the output video.

    Returns:
    ----------
        subprocess.Popen: A subprocess representing the FFmpeg process for output.
    """
    process_args = (
        ffmpeg.input(
            "pipe:", format="rawvideo", pix_fmt="rgb24", s="{}x{}".format(width, height)
        )
        .filter("fps", fps=new_fps, round="up")
        .output(out_filename, pix_fmt="yuv420p")
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(process_args, stdin=subprocess.PIPE)


def read_frame(process1, width, height):
    """
    Read a frame from an FFmpeg process.

    Inputs:
    ----------
        process1 (subprocess.Popen): The FFmpeg process.
        width (int): The width of the video frame.
        height (int): The height of the video frame.

    Returns:
    ----------
        numpy.ndarray or None: The frame as a NumPy array or None if no more frames are available.
    """
    # Note: RGB24 == 3 bytes per pixel.
    frame_size = width * height * 3
    in_bytes = process1.stdout.read(frame_size)
    if len(in_bytes) == 0:
        frame = None
    else:
        assert len(in_bytes) == frame_size
        frame = numpy.frombuffer(in_bytes, numpy.uint8).reshape([height, width, 3])
    return frame


def write_frame(process2, frame):
    """
    Write a frame to an FFmpeg process.

    Inputs:
    ----------
        process2 (subprocess.Popen): The FFmpeg process for output.
        frame (numpy.ndarray): The frame to be written.
    """
    process2.stdin.write(frame.astype(numpy.uint8).tobytes())


def run(in_filename, out_filename, factor):
    """
    Perform frame interpolation on an input video and save the result to an output video.

    Inputs:
    ----------
        in_filename (str): The input video file name.
        out_filename (str): The output video file name.
        factor (int): The interpolation factor (an integer >= 2).
    """
    width, height, fps = get_video_size(in_filename)
    new_fps = fps * factor
    process_input = start_ffmpeg_process_input(in_filename)
    process_output = start_ffmpeg_process_output(out_filename, width, height, new_fps)

    previous_frame = read_frame(process_input, width, height)
    while True:
        write_frame(process_output, previous_frame)
        print("Loading frame...")
        current_frame = read_frame(process_input, width, height)
        if current_frame is None:
            break
        if int(method_args["factor"]) == 2:
            interpolated_frame = interpolate_frame(previous_frame, current_frame)
            write_frame(process_output, interpolated_frame)
        elif int(method_args["factor"]) > 2:
            for interpolated_frame in interpolate_frame(previous_frame, current_frame):
                write_frame(process_output, interpolated_frame)
        previous_frame = current_frame

    process_input.wait()
    process_output.stdin.close()
    process_output.wait()


if __name__ == "__main__":
    ####################### Preprocessing ###################################

    # load and allocate config file
    config = ConfigHandler("reconstruction.smooth_fps")
    s3_args = config.s3
    method_args = config.method

    with CloudFunctionalityReconstruction(s3_args, method_args) as cloud_functionality:
        
        cloud_functionality.preprocess_reconstruction(s3_args, method_args)

        ####################### Check for errors in the args ###################################

        """Options/Args"""
        if int(method_args["factor"]) < 2:
            raise ValueError("Factor must be an integer more than or equal to 2.")

        ###################### Load the model ####################################
        """Load M2M Model"""

        if not torch.cuda.is_available():
            raise Exception("CUDA GPU not detected. CUDA is required.")

        torch.set_grad_enabled(False)

        torch.backends.cudnn.enabled = True
        torch.backends.cudnn.benchmark = True

        netNetwork = m2m.M2M_PWC().cuda().eval()

        netNetwork.load_state_dict(torch.load("./smooth.pkl"))

        ###################### Run the frame interpolation ####################################

        # Loop through all videos that need to be reduced.
        for i in range(len(os.listdir("reduced_videos"))):
            input_video_path = os.path.join(
                "./reduced_videos/", os.listdir("reduced_videos")[i]
            )

            output_video_path = os.path.join(
                "./reconstructed_videos/", os.listdir("reduced_videos")[i]
            )

            run(input_video_path, output_video_path, int(method_args["factor"]))

        ##################### Upload #####################################
        cloud_functionality.upload_reconstruction(s3_args, method_args)

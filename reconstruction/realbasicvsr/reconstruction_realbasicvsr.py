"""
Module to contain the reconstruction technique based off of RealBasicVSR. 4x reconstruction of videos.
"""
import os
import subprocess
import sys
import cv2
import mmcv
import numpy as np
import torch
from mmcv.runner import load_checkpoint
from mmedit.core import tensor2img
from pathlib import Path

from builder import Builder

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality
from utilities import ConfigHandler

VIDEO_EXTENSIONS = (".mp4", ".mov")


def init_model(config, checkpoint=None):
    """
    Initialize a model from config file.

    Inputs
    -------
        config: str
            Config file path or the config object.
        checkpoint: str
            Pretrained model path.

    Returns
    -------
        model : nn.Module
            The constructed model.
    """
    builder = Builder()
    if isinstance(config, str):
        config = mmcv.Config.fromfile(config)

    elif not isinstance(config, mmcv.Config):
        raise TypeError(
            "config must be a filename or Config object, " f"but got {type(config)}"
        )
    config.model.pretrained = None
    config.test_cfg.metrics = None
    model = builder.build_model(config.model, test_cfg=config.test_cfg)
    if checkpoint is not None:
        checkpoint = load_checkpoint(model, checkpoint)

    model.cfg = config  # Save the config in the model for convenience.
    model.eval()

    return model


def realbasicvsr_runner(method_args):
    """
    Method that super resolves videos using pretrained RealBasicVSR model (GAN based).

    Parameters
    ----------
        method_args:
            configparser object.  Parameters defined in ~/config.ini
    """

    # Initialize the model.
    model = init_model(absolute_path_getter("realbasicvsr_x4.py"), method_args['local_model_path'])

    # Read frames from video and create an array of frames.

    for i in range(len(os.listdir("reduced_videos"))):
        input_dir = os.path.join("./reduced_videos/", os.listdir("reduced_videos")[i])

        output_dir = os.path.join(
            "./reconstructed_videos/", os.listdir("reduced_videos")[i]
        )

        # Extract the file extension to see if video or directory was passed in.
        file_extension = os.path.splitext(input_dir)[1]

        # If Input is a video file.
        if file_extension in VIDEO_EXTENSIONS:
            video_reader = mmcv.VideoReader(input_dir)
            inputs = []
            for frame in video_reader:
                inputs.append(np.flip(frame, axis=2))

        # If what was passed in was not a video.
        else:
            raise ValueError('"input_dir" can only be a video or a directory.')

        # Pre-process input frames.
        for i, img in enumerate(inputs):
            img = torch.from_numpy(img / 255.0).permute(2, 0, 1).float()
            inputs[i] = img.unsqueeze(0)
        inputs = torch.stack(inputs, dim=1)

        # Map to cuda, if available.
        cuda_flag = False
        if torch.cuda.is_available():
            model = model.cuda()
            cuda_flag = True

        # Apply super resolution to all of the frames.
        with torch.no_grad():
            if cuda_flag:
                inputs = inputs.cuda()
            outputs = model(inputs, test_mode=True)["output"].cpu()

        # Process the frames outputs and synthesize output video.
        output_dir = os.path.dirname(output_dir)
        mmcv.mkdir_or_exist(output_dir)

        h, w = outputs.shape[-2:]
        fourcc = cv2.VideoWriter_fourcc(*method_args['codec'])
        video_writer = cv2.VideoWriter(output_dir, fourcc, method_args['fps'], (w, h))
        for i in range(0, outputs.size(1)):
            img = tensor2img(outputs[:, i, :, :, :])
            video_writer.write(img.astype(np.uint8))
        video_writer.release()


def absolute_path_getter(file_name):
    """
    Takes in file name, in the same working directory as the 'running' python file (__file__)

    Arguments:
        String: file_name
            name of subject file
    Returns:
        PosixPath: py_path
             Absolute path of file_name
    """
    method_path = Path(__file__)
    abs_path_parent = method_path.parent.absolute()
    py_path = str(abs_path_parent.joinpath(file_name))
    return(py_path)


if __name__ == "__main__":
    cloud_functionality = CloudFunctionality()

    config = ConfigHandler('reconstruction.realbasicvsr')
    s3_args = config.s3
    method_args = config.method

    cloud_functionality.preprocess_reconstruction(s3_args, method_args)

    realbasicvsr_runner(method_args)

    cloud_functionality.postprocess_reconstruction(s3_args, method_args)

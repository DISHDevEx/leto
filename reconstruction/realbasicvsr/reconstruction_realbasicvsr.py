"""
Module to contain the reconstruction technique based off of RealBasicVSR. 4x reconstruction of videos.
"""
import argparse
import glob
import os

import cv2
import mmcv
import numpy as np
import torch
from mmcv.runner import load_checkpoint
from mmedit.core import tensor2img

from builder import Builder


from utilities import CloudFunctionality
from utilities import parse_recon_args

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


def realbasicvsr_runner(args):
    args = parse_args()

    input_dir = "./reduced_videos"
    output_dir = "./reconstructed_videos"
    fps = 25

    # Initialize the model.
    model = init_model("realbasicvsr_x4.py", args.local_model_path)

    # Read frames from video and create an array of frames.

    # Extract the file extension to see if video or directory was passed in.
    file_extension = os.path.splitext(input_dir)[1]

    # If Input is a video file.
    if file_extension in VIDEO_EXTENSIONS:
        video_reader = mmcv.VideoReader(input_dir)
        inputs = []
        for frame in video_reader:
            inputs.append(np.flip(frame, axis=2))

    # If input is a directory.
    elif file_extension == "":
        inputs = []
        input_paths = sorted(glob.glob(f"{input_dir}/*"))
        for input_path in input_paths:
            img = mmcv.imread(input_path, channel_order="rgb")
            inputs.append(img)

    # If what was passed in was neither an input directory or a video.
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
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_dir, fourcc, fps, (w, h))
    for i in range(0, outputs.size(1)):
        img = tensor2img(outputs[:, i, :, :, :])
        video_writer.write(img.astype(np.uint8))
    video_writer.release()


if __name__ == "__main__":
    cloud_functionality = CloudFunctionality()

    args = parse_recon_args()

    cloud_functionality.preprocess(args)

    realbasicvsr_runner()

    cloud_functionality.postprocess(args)

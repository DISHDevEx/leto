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

VIDEO_EXTENSIONS = (".mp4", ".mov")


def parse_args():
    """
    Parses the arguments needed for RealBasicVSR reconstruction module.
    Catalogues: config, checkpoint, input dir, output dir, maximum sequence length, and fps


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent config, checkpoint, input dir, output dir, maximum sequence length, and fps.
    """

    parser = argparse.ArgumentParser(description="Inference script of RealBasicVSR")
    parser.add_argument("input_dir", help="directory of the input video")
    parser.add_argument("output_dir", help="directory of the output video")
    parser.add_argument(
        "--config",
        type=str,
        default="./realbasicvsr_x4.py",
        help="test config file path",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="./RealBasicVSR_x4.pth",
        help="checkpoint file",
    )
    parser.add_argument(
        "--max_seq_len",
        type=int,
        default=None,
        help="maximum sequence length to be processed",
    )
    parser.add_argument(
        "--is_save_as_png", type=bool, default=True, help="whether to save as png"
    )
    parser.add_argument("--fps", type=float, default=25, help="FPS of the output video")
    args = parser.parse_args()

    return args


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


def main():
    args = parse_args()

    # Initialize the model.
    model = init_model(args.config, args.checkpoint)

    # Read frames from video and create an array of frames.
    
    #Extract the file extension to see if video or directory was passed in.
    file_extension = os.path.splitext(args.input_dir)[1]
    
    # If Input is a video file. 
    if file_extension in VIDEO_EXTENSIONS:  
        video_reader = mmcv.VideoReader(args.input_dir)
        inputs = []
        for frame in video_reader:
            inputs.append(np.flip(frame, axis=2))
            
    # If input is a directory. 
    elif file_extension == "":  
        inputs = []
        input_paths = sorted(glob.glob(f"{args.input_dir}/*"))
        for input_path in input_paths:
            img = mmcv.imread(input_path, channel_order="rgb")
            inputs.append(img)
            
    #If what was passed in was neither an input directory or a video.      
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
        if isinstance(args.max_seq_len, int):
            outputs = []
            for i in range(0, inputs.size(1), args.max_seq_len):
                imgs = inputs[:, i : i + args.max_seq_len, :, :, :]
                if cuda_flag:
                    imgs = imgs.cuda()
                outputs.append(model(imgs, test_mode=True)["output"].cpu())
            outputs = torch.cat(outputs, dim=1)
        else:
            if cuda_flag:
                inputs = inputs.cuda()
            outputs = model(inputs, test_mode=True)["output"].cpu()

    #Process the frames outputs and synthesize output video. 
    output_dir = os.path.dirname(args.output_dir)
    mmcv.mkdir_or_exist(output_dir)

    h, w = outputs.shape[-2:]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(args.output_dir, fourcc, args.fps, (w, h))
    for i in range(0, outputs.size(1)):
        img = tensor2img(outputs[:, i, :, :, :])
        video_writer.write(img.astype(np.uint8))
    video_writer.release()


if __name__ == "__main__":
    main()

import subprocess
import argparse
import ffmpeg
import numpy
import torch
import sys
import model.m2m as m2m
import configparser
import logging
import os

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import CloudFunctionality



def interpolate_frame(frame1, frame2):
    """The M2M processing happens here"""
    frame1_np = frame1[:, :, ::-1].astype(numpy.float32) * (1.0 / 255.0)
    frame2_np = frame2[:, :, ::-1].astype(numpy.float32) * (1.0 / 255.0)

    frame1_tensor = torch.FloatTensor(numpy.ascontiguousarray(frame1_np.transpose(2, 0, 1)[None, :, :, :])).cuda()
    frame2_tensor = torch.FloatTensor(numpy.ascontiguousarray(frame2_np.transpose(2, 0, 1)[None, :, :, :])).cuda()

    if int(method_args['factor']) == 2:
        interpolated_frame_tensor = \
            netNetwork(frame1_tensor, frame2_tensor, [torch.FloatTensor([0.5]).view(1, 1, 1, 1).cuda()])[0]
        interpolated_frame_np = (interpolated_frame_tensor.detach().cpu().numpy()[0, :, :, :].
                                 transpose(1, 2, 0)[:, :, ::-1] * 255.0).clip(0.0, 255.0).round().astype(numpy.uint8)
        return interpolated_frame_np
    elif int(method_args['factor']) > 2:
        interpolated_frames_tensor = [torch.FloatTensor([step / int(method_args['factor'])]).view(1, 1, 1, 1).cuda()
                                      for step in range(1, int(method_args['factor']))]
        interpolated_frames = netNetwork(frame1_tensor, frame2_tensor, interpolated_frames_tensor, int(method_args['factor']))
        interpolated_frames_np = [(frame.detach().cpu().numpy()[0, :, :, :].transpose(1, 2, 0)[:, :, ::-1] * 255.0).
                                  clip(0.0, 255.0).round().astype(numpy.uint8) for frame in interpolated_frames]
        return interpolated_frames_np


def get_video_size(filename):
    probe = ffmpeg.probe(filename)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    return width, height


def start_ffmpeg_process_input(in_filename):
    process_args = (
        ffmpeg
        .input(in_filename)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .compile()
    )
    return subprocess.Popen(process_args, stdout=subprocess.PIPE)


def start_ffmpeg_process_output(out_filename, width, height):
    process_args = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height))
        .filter('fps', fps=method_args['fps'], round='up')
        .output(out_filename, pix_fmt='yuv420p')
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(process_args, stdin=subprocess.PIPE)


def read_frame(process1, width, height):
    # Note: RGB24 == 3 bytes per pixel.
    frame_size = width * height * 3
    in_bytes = process1.stdout.read(frame_size)
    if len(in_bytes) == 0:
        frame = None
    else:
        assert len(in_bytes) == frame_size
        frame = (
            numpy
            .frombuffer(in_bytes, numpy.uint8)
            .reshape([height, width, 3])
        )
    return frame


def write_frame(process2, frame):
    process2.stdin.write(
        frame
        .astype(numpy.uint8)
        .tobytes()
    )


def run(in_filename, out_filename):
    width, height = get_video_size(in_filename)
    process_input = start_ffmpeg_process_input(in_filename)
    process_output = start_ffmpeg_process_output(out_filename, width, height)

    previous_frame = read_frame(process_input, width, height)
    while True:
        write_frame(process_output, previous_frame)
        print("Loading frame...")
        current_frame = read_frame(process_input, width, height)
        if current_frame is None:
            break
        if int(method_args['factor']) == 2:
            interpolated_frame = interpolate_frame(previous_frame, current_frame)
            write_frame(process_output, interpolated_frame)
        elif int(method_args['factor']) > 2:
            for interpolated_frame in interpolate_frame(previous_frame, current_frame):
                write_frame(process_output, interpolated_frame)
        previous_frame = current_frame

    process_input.wait()
    process_output.stdin.close()
    process_output.wait()


if __name__ == '__main__':
    
    ####################### Preprocessing ###################################

    cloud_functionality = CloudFunctionality()

    # load and allocate config file
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    config.read('../../config.ini')
    s3_args = config['DEFAULT']
    method_args = config['reconstruction.recon_args']
    logging.info("successfully loaded config file")

    cloud_functionality.preprocess(method_args, s3_args)

    ####################### Check for errors in the args ###################################
    
    """Options/Args"""
    if int(method_args['factor']) < 2:
        raise ValueError('Factor must be an integer more than or equal to 2.')

    ###################### Load the model ####################################
    """Load M2M Model"""

    if not torch.cuda.is_available():
        raise Exception("CUDA GPU not detected. CUDA is required.")

    torch.set_grad_enabled(False)

    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    netNetwork = m2m.M2M_PWC().cuda().eval()

    netNetwork.load_state_dict(torch.load('./smooth.pkl'))

    ###################### Run the frame interpolation ####################################

    # Loop through all videos that need to be reduced.
    for i in range(len(os.listdir("reduced_videos"))):
        input_video_path = os.path.join(
            "./reduced_videos/", os.listdir("reduced_videos")[i]
        )

        output_video_path = os.path.join(
            "./reconstructed_videos/", os.listdir("reduced_videos")[i]
        )

        run(input_video_path, output_video_path)

    ##################### Postprocessing #####################################
    cloud_functionality.postprocess(method_args, s3_args)
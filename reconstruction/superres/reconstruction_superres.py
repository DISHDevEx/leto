'''
Module that enhances video resolution using Deep Neural Networks.
'''
import os
import sys
import cv2
import boto3
import argparse
import subprocess
from cv2 import dnn_superres
from aEye import Aux

# While working locally, uncomment the following code -
# # get git repo root level
# root_path = subprocess.run(['git', 'rev-parse',  '--show-toplevel'],
#                             capture_output=True, text=True, check=False)\
#                       .stdout.rstrip('\n')
# #add git repo path to use all libraries
# sys.path.append(root_path)
# from utilities import download_model

# While working on EC2, use the following code -
from download_model import download_model

def parse_args():
    """
    Parses the arguments needed for Super Resolution reconstruction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
            codec, resolution, model bucket, model prefix and algorithm.

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix, codec, resolution, model bucket, model prefix and algorithm.
    """
    # Inference script of opencv video upscaler
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_bucket_s3',
                        type =str,
                        help ='s3 bucket of the input video',
                        default = "leto-dish")

    parser.add_argument("--input_prefix_s3",
                        type = str,
                        help = "s3 prefix of the input video",
                        default = 'reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/')

    parser.add_argument("--output_bucket_s3",
                        type=str,
                        default = "leto-dish",
                        help = "s3 bucket of the output video")

    parser.add_argument("--output_prefix_s3",
                        type = str,
                        default = "reconstructed-videos/benchmark/superres/car/",
                        help ="s3 prefix of the output video")

    parser.add_argument("--codec",
                        type = str,
                        default = 'mp4v',
                        help ="video codec")

    parser.add_argument("--resolution",
                        type = tuple,
                        default = (1920, 1080),
                        help ="desired video resolution")

    parser.add_argument("--model_bucket_s3",
                        type = str,
                        default = "leto-dish",
                        help = "s3 bucekt of the pre-trained model")

    parser.add_argument("--model_prefix_s3",
                        type = str,
                        default = "pretrained-models/fsrcnn_x4.pb",
                        help = "s3 prefix of the pre-trained model")

    parser.add_argument("--algorithm",
                        type = str,
                        default = "fsrcnn",
                        help="algorithm of the pre-trained model")

    parser.add_argument("--model_path",
                        type = str,
                        default = "model.pb",
                        help="local path to save pre-trained model")

    args = parser.parse_args()

    return args

def superres_preprocess():
    '''
    Method that downloads videos and model from s3 onto local environment.
    '''
    args = parse_args()
    aux = Aux()

    os.mkdir('./reduced_videos')
    os.mkdir('./reconstructed_videos')

    reduced_video_list = aux.load_s3(args.input_bucket_s3, args.input_prefix_s3)

    aux.execute_label_and_write_local(reduced_video_list, 'reduced_videos')

    # Download model
    download_model(args.model_path, args.model_bucket_s3, args.model_prefix_s3)

def superres_video():
    '''
    Function that enhances video resolution using Deep Neural Networks.
    '''

    args = parse_args()

    for i in range(len(os.listdir('reduced_videos'))):
        input_video_path = os.path.join('./reduced_videos/',os.listdir('reduced_videos')[i])
        superres_video_path = os.path.join('./reconstructed_videos/',os.listdir('reduced_videos')[i])
        input_video = cv2.VideoCapture(input_video_path)
        fourcc = cv2.VideoWriter_fourcc(*args.codec)
        fps = input_video.get(cv2.CAP_PROP_FPS)
        superres_video = cv2.VideoWriter(superres_video_path, fourcc, fps, args.resolution)

        # Create an instance of DNN Super Resolution implementation class
        model = dnn_superres.DnnSuperResImpl_create()
        model.readModel('model.pb')
        model.setModel(args.algorithm, 4)

        while input_video.isOpened():
            ret, frame = input_video.read()
            if not ret:
                break

            result = model.upsample(frame)

            # Resize frame
            resized = cv2.resize(result, args.resolution, interpolation = cv2.INTER_LANCZOS4)

            # Write resized frame to the output video file
            superres_video.write(resized)

            # Closing the video by Escape button
            if cv2.waitKey(10) == 27:
                break

        # Release video capture and writer objects
        input_video.release()
        superres_video.release()

def superres_postprocess():
    '''
    Method that loads reconstructed video using superres_video method onto s3 and deletes
    temporary video folders and model file.
    '''

    aux = Aux()
    args = parse_args()

    # Load reconstructed video files
    reconstructed_video_list = aux.load_local('./reconstructed_videos')

    aux.set_local_path('./reconstructed_videos')

    # Upload reconstructed video files to s3
    aux.upload_s3(reconstructed_video_list, bucket = args.output_bucket_s3, prefix = args.output_prefix_s3)

    # Delete reconstructed_videos folder from local
    aux.clean()

    aux.set_local_path('./reduced_videos')

    # Delete reduced_videos folder from local
    aux.clean()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

    #After cleaning videos, delete the pretrained model as well.
    os.remove(args.model_path)

if __name__ == '__main__':
    superres_preprocess()
    superres_video()
    superres_postprocess()
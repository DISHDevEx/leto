'''
Module that enhances video resolution using Deep Neural Networks.
'''
import os
import sys
import cv2
import boto3
import argparse
import subprocess


# get git repo root level
root_path = subprocess.run(['git', 'rev-parse',  '--show-toplevel'],
                            capture_output=True, text=True, check=False)\
                      .stdout.rstrip('\n')
#add git repo path to use all libraries
sys.path.append(root_path)

from utilities import download_model

def parse_args():
    """
    Parses the arguments needed for reconstruction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
            codec, resolution, model bucket, model prefix and algorithm.

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix, codec, resolution, model bucket, model prefix and algorithm.
    """

    parser = argparse.ArgumentParser(description="Inference script of upscaler")

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

    parser.add_argument("--model_bucket_s3",
                        type = str,
                        default = "leto-dish",
                        help = "s3 bucket of the pre-trained model")

    parser.add_argument("--model_prefix_s3",
                        type = str,
                        default = "pretrained-models/fastsrgan.h5",
                        help = "s3 prefix of the pre-trained model")

    parser.add_argument("--local_model_path",
                        type = str,
                        default = "fastsrgan.h5",
                        help="local path to save pre-trained model")

    parser.add_argument("--local_model_path",
                    type = str,
                    default = "fastsrgan.h5",
                    help="local path to save pre-trained model")

    parser.add_argument("--clean_model",
                    type=str,
                    default = "True",
                    help= "String to indicate to clean video or not  input video")

    args = parser.parse_args()

    return args



def superres_video(args):
    '''
    Function that enhances video resolution using Deep Neural Networks.
    '''

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

if __name__ == '__main__':
    args = parse_args()

    superres_preprocess(args)
    superres_video(args)
    superres_postprocess(args)
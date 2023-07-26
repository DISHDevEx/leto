'''
Module that upscales video using openCV.
'''
import subprocess
import argparse
import cv2
import os
import boto3
import static_ffmpeg
from aEye import Aux

def parse_args():
    """
    Parses the arguments needed for OpenCV reconstruction module.
    Catalogues: input bucket, input s3 prefix, output bucket, output s3 prefix and scaling resolution


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input bucket, input s3 prefix, output bucket, output s3 prefix and scaling resolution.
    """

    parser = argparse.ArgumentParser(description="Inference script of opencv video upscaler")

    parser.add_argument('--input_bucket_s3',
                        type=str,
                        help='s3 bucket of the input video',
                        default = "leto-dish")

    parser.add_argument("--input_prefix_s3",
                        type=str,
                        help= "s3 prefix of the input video",
                        default = "reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/")

    parser.add_argument("--output_bucket_s3",
                        type=str,
                        default = "leto-dish",
                        help= "s3 bucket of the output video")

    parser.add_argument("--output_prefix_s3",
                        type = str,
                        default = "reconstructed-videos/benchmark/opencv/car/",
                        help="s3 prefix of the output video")

    parser.add_argument("--scaling_resolution",
                        type = tuple,
                        default = (1920, 1080),
                        help="output video resolution")

    args = parser.parse_args()

    return args

def upscale_preprocess():
    '''
    Method that downloads videos from s3 onto local environment.
    '''
    args = parse_args()
    aux = Aux()
    
    os.mkdir('./reduced_videos')
    os.mkdir('./reconstructed_videos')
    
    reduced_video_list = aux.load_s3(args.input_bucket_s3, args.input_prefix_s3)
    
    aux.execute_label_and_write_local(reduced_video_list, 'reduced_videos')
    
def upscale_video():
    '''
    Method that upscales video using opencv and merges audio with the upscaled video
    '''
    
    args = parse_args()
    
    for i in range(len(os.listdir('reduced_videos'))):
        input_video_path = os.path.join('./reduced_videos/',os.listdir('reduced_videos')[i])
        upscaled_video_path = os.path.join('./reconstructed_videos/',os.listdir('reduced_videos')[i])
        input_video = cv2.VideoCapture(input_video_path)
        fps = input_video.get(cv2.CAP_PROP_FPS)
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        upscaled_video = cv2.VideoWriter(upscaled_video_path, codec, fps, args.scaling_resolution)
        while input_video.isOpened():
            ret, frame = input_video.read()
            if ret is True:
                resized_frame = cv2.resize(frame,args.scaling_resolution,fx=0,fy=0, interpolation = cv2.INTER_LANCZOS4)
                upscaled_video.write(resized_frame)
            else:
                break
        P = subprocess.Popen(["static_ffmpeg", "-show_streams", "-print_format", "json", input_video_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        streams = P.communicate()[0]
        streams = streams.decode('utf-8')
        if 'audio' in streams.lower():
            # Extract audio from source video
            subprocess.call(["static_ffmpeg", "-i", input_video_path, "sourceaudio.mp3"], shell=True)
            # Merge source audio and upscaled video
            subprocess.call(["static_ffmpeg", "-i", upscaled_video_path, "-i",  "sourceaudio.mp3", "-map",
                            "0:0", "-map", "1:0", upscaled_video_path], shell=True)
        else:
            pass

        input_video.release()
        upscaled_video.release()
        
def upscale_postprocess():
    '''
    Method that loads reconstructed video using upscale_video method onto s3 and deletes
    temporary files and folders.
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
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    upscale_preprocess()
    upscale_video()
    upscale_postprocess()
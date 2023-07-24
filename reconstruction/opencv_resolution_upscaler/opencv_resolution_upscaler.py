'''
Module that upscales video using openCV.
'''
import subprocess
import argparse
import cv2
import os
import boto3
import static_ffmpeg
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
                        default = 'reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4')

    parser.add_argument("--output_bucket_s3",
                        type=str,
                        default = "leto-dish",
                        help= "s3 bucket of the output video")

    parser.add_argument("--output_prefix_s3",
                        type = str,
                        default = "reconstructed-videos/benchmark/opencv/car/video_benchmark_car_upscaled.mp4",
                        help="s3 prefix of the output video")

    parser.add_argument("--scaling_resolution",
                        type = tuple,
                        default = (1920, 1080),
                        help="output video resolution")

    args = parser.parse_args()

    return args

def upscale_video():
    '''
    Method that upscales video using opencv and merges audio with the scaled video
    if original video has an audio stream.
    '''

    args = parse_args()

    s3_client = boto3.client('s3')

    # input_url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': args.input_bucket_s3, 'Key': args.input_prefix_s3})
    input_video_path = 'input.mp4'
    upscaled_video_path = 'output.mp4'

    s3_client.download_file(args.input_bucket_s3, args.input_prefix_s3, input_video_path)

    input_video = cv2.VideoCapture(input_video_path)
    fps = input_video.get(cv2.CAP_PROP_FPS)
    total_frames = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    scaled_video = cv2.VideoWriter(upscaled_video_path, codec, fps, args.scaling_resolution)
    while input_video.isOpened():
        ret, frame = input_video.read()
        if ret is True:
            resized_frame = cv2.resize(frame,args.scaling_resolution,fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            scaled_video.write(resized_frame)
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

    with open(upscaled_video_path, 'rb') as file:
        s3_client.put_object(Body=file, Bucket=args.output_bucket_s3, Key=args.output_prefix_s3)

    input_video.release()
    scaled_video.release()

    os.remove(input_video_path)
    os.remove(upscaled_video_path)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    upscale_video()
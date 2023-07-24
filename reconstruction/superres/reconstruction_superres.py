'''
Module that enhances video resolution using Deep Neural Networks.
'''
import os
import sys
import cv2
import boto3
import argparse
from cv2 import dnn_superres

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

    parser = argparse.ArgumentParser(description="Inference script of opencv video upscaler")

    parser.add_argument('--input_bucket_s3',
                        type =str,
                        help ='s3 bucket of the input video',
                        default = "leto-dish")

    parser.add_argument("--input_prefix_s3",
                        type = str,
                        help = "s3 prefix of the input video",
                        default = 'reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4')

    parser.add_argument("--output_bucket_s3",
                        type=str,
                        default = "leto-dish",
                        help = "s3 bucket of the output video")

    parser.add_argument("--output_prefix_s3",
                        type = str,
                        default = "reconstructed-videos/benchmark/super_res/car/benchmark_superres_fsrcnn.mp4",
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

    args = parser.parse_args()

    return args

def video_superres():
    '''
    Function that enhances video resolution using Deep Neural Networks.
    '''

    args = parse_args()
    s3_client = boto3.client('s3')
    enhanced_video_path = 'output.mp4'
    input_url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': args.input_bucket_s3, 'Key': args.input_prefix_s3})
    input_video = cv2.VideoCapture(input_url)
    fourcc = cv2.VideoWriter_fourcc(*args.codec)
    fps = input_video.get(cv2.CAP_PROP_FPS)
    enhanced_video = cv2.VideoWriter(enhanced_video_path, fourcc, fps, args.resolution)

    # Download model
    model_path = 'model.pb'
    model = s3_client.download_file(Bucket = args.model_bucket_s3, Key = args.model_prefix_s3, Filename = model_path)
    # Create an instance of DNN Super Resolution implementation class
    model = dnn_superres.DnnSuperResImpl_create()
    model.readModel(model_path)
    model.setModel(args.algorithm, 4)

    while input_video.isOpened():
        ret, frame = input_video.read()
        if not ret:
            break

        result = model.upsample(frame)

        # Resized image
        resized = cv2.resize(result, args.resolution, interpolation = cv2.INTER_AREA)

        # Write the resized frame to the output video file
        enhanced_video.write(resized)

        # Closing the video by Escape button
        if cv2.waitKey(10) == 27:
            break

    with open(enhanced_video_path, 'rb') as file:
        s3_client.put_object(Body=file, Bucket=args.output_bucket_s3, Key=args.output_prefix_s3)

    # Release the video capture and writer objects
    input_video.release()
    enhanced_video.release()

    os.remove(enhanced_video_path)
    os.remove(model_path)

    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_superres()
"""
Module to contain the handler function for the YOLO lambda function. This file is what the lambda functions runs.
"""
import boto3
import os
from yolo import Yolo
from aEye import Video
from pipeline import pipeline
import urllib.parse


def handler(event, context):
    """
    Current version of the lambda function reads from an s3 bucket and applies yolo's object detection model on the files.

    Parameters
    ----------
        event : dictionary
            The s3 path information for mediapipe's object detection model to be applied on.
    """
    print("Loading function")

    s3_client = boto3.client("s3")

    yolo_model = Yolo()
    yolo_model.load_model_weight("yolov8s.pt")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )

    try:
        video = Video(bucket=bucket, key=key)

        yolo_output_video = os.path.join(
            "/tmp", os.path.basename("yolo_" + video.get_title())
        )

        mAC = pipeline(video.get_file().strip("'"), yolo_model, yolo_output_video)

        video_location = f's3://{bucket}/{key}'

        return {video_location : mAC }
        

    except Exception as e:
        print(e)
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, bucket
            )
        )
        raise e

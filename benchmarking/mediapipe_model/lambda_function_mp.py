"""
Module to contain the handler function for the MediaPipe lambda function. This file is what the lambda functions runs.
"""
import os
from object_detection import object_detection

import boto3
import os
from aEye import Video
import urllib.parse


def handler(event, context):
    """
    Current version of the lambda function reads from an s3 bucket and applies mediapipe's object detection model on the files.

    Parameters
    ----------
        event : dictionary
            The s3 path information for mediapipe's object detection model to be applied on.
    """
    print("Loading function")
    print(os.system("ls"))
    s3_client = boto3.client("s3")

    mp_model = os.path.basename("efficientdet_lite0.tflite")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )

    try:
        video = Video(bucket=bucket, key=key)

        mp_output_video = os.path.join(
            "/tmp", os.path.basename("mp_" + video.get_title())
        )

        object_detection(mp_model, video.get_file().strip("'"), mp_output_video)

        s3_client.upload_file(
            mp_output_video, "leto-dish", f"object_detection/mp_{video.get_title()}"
        )

    except Exception as e:
        print(e)
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, bucket
            )
        )
        raise e

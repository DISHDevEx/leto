"""
Module to contain the handler function for the MediaPipe lambda function. This file is what the lambda functions runs.
"""
import os
from object_detection import object_detection

import boto3
import os

import urllib.parse

s3_client = boto3.client("s3")
dynamodb = boto3.resource('dynamodb')

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

    score = {}
    mp_model = os.path.basename("efficientdet_lite0.tflite")

    bucket_name = event["bucket_name"]
    folder_path = event["folder_path"]
    dynamodb_table = event["dynamodb_table"]

    try:
        # Retrieve the list of object keys from the specified bucket
        s3_keys = list_object_keys(bucket_name, folder_path)

        for key in s3_keys:
            # Download the video from S3 to Lambda's /tmp directory
            local_filename = '/tmp/' + os.path.basename(key)
            s3_client.download_file(bucket_name, key, local_filename)

            # Process the downloaded video

            mAC = object_detection(mp_model,local_filename, "")
            if len(mAC):
                mean_average_confidence = sum(mAC) / len(
                    mAC)
            video_location = f's3://{bucket_name}/{key}'
            # Optionally, you can delete the local file to save space
            os.remove(local_filename)
            score.update({video_location: mean_average_confidence})

            table_name = dynamodb_table

            table = dynamodb.Table(table_name)
            try:
                response = table.put_item(Item={'video_location':  video_location, 'score': str(mean_average_confidence)})
                print('Uploaded location:', video_location)
            except Exception as e:
                print('Error uploading metric:', mean_average_confidence, e)

            print({video_location: mean_average_confidence})
        return score


    except Exception as e:
        print(e)
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                folder_path, bucket_name
            )
        )
        raise e

def list_object_keys(bucket_name, folder_path):
    keys = []
    response = s3_client.list_objects_v2(Bucket=bucket_name,Prefix=folder_path)
    if 'Contents' in response:
        for obj in response['Contents']:
            keys.append(obj['Key'])
    return keys[1:-1]

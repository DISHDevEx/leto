import boto3
import os
from yolo import Yolo
from aEye import Video
from pipeline import pipeline
import urllib.parse

def handler(event, context):

    print('Loading function')

    s3_client = boto3.client('s3')

    yolo_model = Yolo()
    yolo_model.load_model_weight('yolov8s.pt')

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        video = Video(bucket=bucket, key=key)

        yolo_output_video = os.path.join("/tmp", os.path.basename('yolo_' + video.get_title()))

        pipeline(video.get_file().strip("'"
                                        ), yolo_model, yolo_output_video)

        s3_client.upload_file(yolo_output_video, "leto-dish", f"object_detection/yolo_{video.get_title()}")

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

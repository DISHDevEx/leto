# try:
#     from mediapipe_model import object_detection
#     print('1')
# except:
#     pass

import os
import sys
print(os.system('ls'))
from object_detection import object_detection2
import sys
import boto3
import os
from aEye import Video
import urllib.parse

# input_video_path = os.environ.get('input_video_path')
# output_video_path = os.environ.get('output_video_path')


def handler(event, context):

    print('Loading function')

    s3_client = boto3.client('s3')

    mp_model = os.path.basename("efficientdet_lite0.tflite")

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        video = Video(bucket=bucket, key=key)

        mp_output_video = os.path.join("/tmp", os.path.basename('mp_' + video.get_title()))

        object_detection2(mp_model, video.get_file(), mp_output_video)

        s3_client.upload_file(mp_output_video, "leto-dish", f"object_detection/mp_{video.get_title()}")

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

from aEye import reduction
import sys
import boto3
import os
from aEye.auxiliary import Aux
import logging


def app():

    logging.info('succesfully loaded function')

    aux=Aux()
    video_list = aux.load_s3(bucket = 'aeye-data-bucket', prefix = 'input_video/')
    reduction(video_list)
    out = aux.execute_label_and_write_local(video_list)
    aux.upload_s3(video_list, "leto-dish", "reduction/")
    aux.clean()

    return 'video reduction completed on ' + sys.version + '!'

app()
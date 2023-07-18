from fps_bitrate import fps_bitrate
from aEye import Aux

import sys
import logging


def handler(event, context):

    logging.info('succesfully loaded function')

    aux=Aux()
    
    try:
        video_list = aux.load_s3(bucket = 'aeye-data-bucket', prefix = 'input_video/')
    except Exception as e:
        print(e)
        logging.warning(f"unable to load video list from s3.")
    
    fps_bitrate(video_list)
    out = aux.execute_label_and_write_local(video_list)
    aux.upload_s3(video_list, "leto-dish", "reduction/")
    aux.clean()

    return 'video reduction completed on ' + sys.version + '!'
from fps_bitrate import fps_bitrate
from aEye import Aux

import sys
import logging


def app_fps_bitrate():
    """
    Runner method for fps_bitrate.fps_bitrate().  This method abstracts some of the
    interaction with S3 and AWS away from fps_bitrate.

    Input and Output S3 paths are hard coded in this version; this can be abstracted in
    future versions to allow for dynamic Input and Output allocation.

    Input Video S3 Path: aeye-data-bucket/input_video/
    Output Video S3 Path: leto-dish/reduction/fps_bitrate/

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.
    """

    logging.info("successfully loaded function")

    aux = Aux()

    try:
        video_list = aux.load_s3(bucket="aeye-data-bucket", prefix="input_video/")
    except Exception as e:
        print(e)
        logging.warning(
            f"unable to load video list from s3; ensure AWS credentials have been provided."
        )

    fps_bitrate(video_list)
    out = aux.execute_label_and_write_local(video_list)
    aux.upload_s3(video_list, "leto-dish", "reduced-videos/fps_bitrate/")
    aux.clean()

    return logging.info("video reduction completed on " + sys.version + ".")


if __name__ == "__main__":
    app_fps_bitrate()

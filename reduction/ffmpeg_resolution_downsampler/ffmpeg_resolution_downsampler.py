"""
Script to change the resolution of a video via ffmpeg.
"""

import logging
import subprocess
import sys

from aEye import Labeler
from aEye import Aux

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler



def main():
    """
    Runner method for ffmpeg resolution downsampler.  This method abstracts some of the
    interaction with S3 and AWS away from ffmpeg.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.
    """

    logging.info("running reduction module")
    
    aux = Aux()
    cloud_functionality = CloudFunctionality()
    labeler = Labeler()

    config = ConfigHandler('reduction.ffmpeg_resolution_downsampler')
    s3_args = config.s3
    method_args = config.method

 
    
    video_list_s3 = cloud_functionality.preprocess_reduction(s3_args, method_args )
    
    downsampled_video = labeler.change_resolution(
        video_list_s3, method_args['quality'], method_args['algorithm']
    )
    aux.execute_label_and_write_local(downsampled_video,path=method_args['temp_path'])
    cloud_functionality.postprocess_reduction(s3_args, method_args)


if __name__ == "__main__":
    main()

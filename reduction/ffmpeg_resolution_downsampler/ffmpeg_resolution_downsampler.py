import argparse
import logging

from aEye import Video
from aEye import Labeler
from aEye import Aux

import os



def parse_args():
    """
    Parses the arguments needed for ffmpeg based reduction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket and output s3 prefix.


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent config, checkpoint, input dir, output dir, maximum sequence length, and fps.
    """

    parser = argparse.ArgumentParser(description="Inference script of ffmpeg resolution downsampler")
    parser.add_argument("--input_bucket_s3", 
                        type=str,
                        default = "leto-dish",
                        help= "s3 bucket of the input video")
    
    parser.add_argument("--input_prefix_s3", 
                        type=str,
                        default = "original-videos/benchmark/car/",
                        help= "s3 prefix of the input video")
    
    parser.add_argument("--output_bucket_s3", 
                        type=str,
                        default = "leto-dish",
                        help= "s3 bucket of the input video")
    
    parser.add_argument("--output_prefix_s3", 
                        type = str,
                        default = "reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/",
                        help="s3 prefix of the output video")
    
    args = parser.parse_args()
    
    return args

def main():
    logging.info("running reduction module")
    
    
    args = parse_args()
    
    aux = Aux()
    
    labeler = Labeler()
    
    video_list_s3 = aux.load_s3(bucket = args.input_bucket_s3, prefix = args.input_prefix_s3)
    
    downsampled_video = labeler.change_resolution(video_list_s3,"360p")
    
    aux.execute_label_and_write_local(downsampled_video)
    
    aux.upload_s3(downsampled_video, bucket = args.output_bucket_s3, prefix =args.output_prefix_s3 )
    
    aux.clean()
    

if __name__ == "__main__":
    main()

import argparse
import logging

from aEye import Video
from aEye import Labeler
from aEye import Aux

from builder import Builder

import os



def parse_args():
    """
    Parses the arguments needed for RealBasicVSR reconstruction module.
    Catalogues: config, checkpoint, input dir, output dir, maximum sequence length, and fps


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent config, checkpoint, input dir, output dir, maximum sequence length, and fps.
    """

    parser = argparse.ArgumentParser(description="Preprocessing script for RealBasicVSR in Leto")
    parser.add_argument("--input_bucket_s3", 
                        type=str,
                        default = "leto-dish",
                        help= "s3 bucket of the input video")
    
    parser.add_argument("--input_prefix_s3", 
                        type=str,
                        default = "reduced-videos/benchmark/ffmpeg-resolution-downsampler/",
                        help= "s3 prefix of the input video")
    
    parser.add_argument("--model_bucket_s3", 
                        type=str,
                        default = "leto-dish",
                        help= "s3 bucket of the RealBasicVSR pretrained model")
    
    parser.add_argument("--model_prefix_key_s3", 
                        type=str,
                        default = "pretrained-models/RealBasicVSR_x4.pth",
                        help= "s3 prefix and key of the RealBasicVSR pretrained model")
    
    

    
    args = parser.parse_args()
    
    return args

def main():
    logging.info("running post processing for RealBasicVSR")
    
    args = parse_args()
    
    builder = Builder()
    
    aux = Aux()
    
    
    os.mkdir("./reduced_videos")
    os.mkdir("./reconstructed_videos")
    
    builder.download_model("./RealBasicVSR_x4.pth",args.model_bucket_s3,args.model_prefix_key_s3)
    
    video_list_s3 = aux.load_s3(bucket = args.input_bucket_s3, prefix = args.input_prefix_s3)
    
    aux.execute_label_and_write_local(video_list_s3,path = "./reduced_videos")
    

if __name__ == "__main__":
    main()

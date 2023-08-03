
"""
Module contains the cv2 jpg quality compression method and reencode cv2 video using ffmpeg.

"""
import subprocess
import argparse 
import static_ffmpeg
import cv2
import os
import logging
import sys
from aEye import Aux

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)



def parse_args():
    """
    Parses the arguments needed for Super Resolution reconstruction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket, output s3 prefix,
            quality, crf, and temp path.

    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket,
            output s3 prefix, quality, crf, and temp path.
    """

    parser = argparse.ArgumentParser(description="Inference script of opencv video upscaler")

    parser.add_argument('--input_bucket_s3',
                        type =str,
                        help ='s3 bucket of the input video',
                        default = "leto-dish")

    parser.add_argument("--input_prefix_s3",
                        type = str,
                        help = "s3 prefix of the input video",
                        default = 'original-videos/benchmark/car/')

    parser.add_argument("--output_bucket_s3",
                        type=str,
                        default = "leto-dish",
                        help = "s3 bucket of the output video")

    parser.add_argument("--output_prefix_s3",
                        type = str,
                        default = "reduced-videos/cv2_compression/",
                        help ="s3 prefix of the output video")

    parser.add_argument("--temp_path",
                        type = str,
                        default = 'temp',
                        help ="A temp folder to store video from uploading to s3")

    parser.add_argument("--quality",
                        type = int,
                        default = 15,
                        help="The compression rate for cv2 to apply, 100 is for best video quality, 0 is for the worse video quality ")
    
    parser.add_argument("--crf",
                        type = int,
                        default = 28,
                        help="the constant rate factor for ffmpeg to encode the video, the lower value results in higher quality. The range is 0-51")

    args = parser.parse_args()

    return args


def cv2_jpg_compress(video, path = "temp" , quality = 15, crf = 28):

    # Create a VideoCapture object
    cap = cv2.VideoCapture(video.get_presigned_url().strip("'"))
    
    # Check if video opened successfully
    if (cap.isOpened() == False): 
        print("Unable to read video ")
    
    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    # We convert the resolutions from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)
    title = video.get_title()
    

    #make a temp_path to store cv2 video
    os.mkdir(f'{path}_cv2')

    out = cv2.VideoWriter(f"{path}_cv2/compressed_" + title,cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width,frame_height))
    
    index = 0
    while(True):

        ret, frame = cap.read()
           
        if ret == True: 
            #compress the jpg quality with cv2
            enc = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])[1]
            out.write(cv2.imdecode(enc,cv2.IMREAD_COLOR) )
            
            index +=1
    # Break the loop
        else:
            break 
            
    logging.info(f"successfully compressed {title} with cv2 jpeg quality rate of {quality}")

    cap.release()
    out.release()

    #using ffmpeg to reencode video with h264 format with crf value
    cmd = f"static_ffmpeg -y -i {path}_cv2/compressed_{title} -c:v libx264  -crf {crf} -preset slow {path}/compressed_{title}"
    subprocess.run(cmd, shell=True)

    
    logging.info(f"successfully reencode {title} into h264 format with the crf of {crf}")
    
    os.remove(f'{path}_cv2/compressed_{title}')
    os.rmdir(f'{path}_cv2')


def main():
    
    args = parse_args()
    aux = Aux()

    os.mkdir(args.temp_path)

    video_list  = aux.load_s3(args.input_bucket_s3, args.input_prefix_s3)
    #compress each and store in temp_path
    for video in video_list:
        cv2_jpg_compress(video, args.temp_path, args.quality, args.crf) 

    #use Aux to easily load, upload and clean up  
    aux = Aux()
    result = aux.load_local(args.temp_path)
    aux.upload_s3(result,bucket=args.output_bucket_s3, prefix=args.output_prefix_s3)

    aux.clean()

if __name__ == "__main__":
    main()

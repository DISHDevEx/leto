"""
Module contains the cv2 jpg quality reduction method and reencode cv2 video using ffmpeg.

"""
import subprocess
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

from utilities import ConfigHandler


def cv2_jpg_reduction(video_list, path="temp", quality=15, crf=28):
    for video in video_list:
        # Create a VideoCapture object
        cap = cv2.VideoCapture(video.get_file().strip("'"))

        # Check if video opened successfully
        if cap.isOpened() == False:
            print("Unable to read video ")

        # Default resolutions of the frame are obtained.The default resolutions are system dependent.
        # We convert the resolutions from float to integer.
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)
        title = video.get_title()

        # make a temp_path to store cv2 video
        # this is needed because ffmpeg cant edit same file in place
        os.mkdir(f"{path}_cv2")

        out = cv2.VideoWriter(
            f"{path}_cv2/" + title+"test_label",
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (frame_width, frame_height),
        )

        index = 0
        while True:
            ret, frame = cap.read()

            if ret == True:
                # compress the jpg quality with cv2
                enc = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])[1]
                out.write(cv2.imdecode(enc, cv2.IMREAD_COLOR))

                index += 1
            # Break the loop
            else:
                break

        logging.info(f"successfully reduce {title} with cv2 jpeg quality rate of {quality}")

        cap.release()
        out.release()

        # using ffmpeg to reencode video with h264 format with crf value
        cmd = f"static_ffmpeg -y -i {path}_cv2/{title} -c:v libx264  -crf {crf} -preset slow {path}/{title}"
        subprocess.run(cmd, shell=True)

        logging.info(
            f"successfully reencode {title} into h264 format with the crf of {crf}"
        )

        os.remove(f"{path}_cv2/{title}")
        os.rmdir(f"{path}_cv2")


def main():
   
    config = ConfigHandler('reduction.cv2_jpg_reduction')
    s3_args = config.s3
    method_args = config.method

    cloud_functionality = CloudFunctionality()


    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args )
    
    # reduce each and store in temp_path
    cv2_jpg_reduction(video_list, method_args['temp_path'], method_args.getint('quality'), method_args.getint('crf'))
    
    cloud_functionality.postprocess_reduction(s3_args, method_args)
    



if __name__ == "__main__":
    main()



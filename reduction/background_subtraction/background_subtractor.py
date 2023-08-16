import cv2
from aEye import Aux
import logging
import os
from pathlib import Path

import subprocess
import time
import sys
from moviepy.editor import VideoFileClip

root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
def background_subtractor(input_folder, output_folder):
    ''' This code helps to extract background from the video 
    Video works usually well on the videos with static background '''
    
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize video capture
    for video in os.listdir(input_folder):
        video_path = os.path.join(input_folder, video)
        capture = cv2.VideoCapture(video_path)

        # Get the video's frame width, height, and frames per second
        frame_width = int(capture.get(3))
        frame_height = int(capture.get(4))
        fps = int(capture.get(cv2.CAP_PROP_FPS))
        video_name = Path(video).stem

        # Define the codec and create a VideoWriter object for the masked video
        output_filename = os.path.join(output_folder, video_name + "_masked.mp4")
        codec = cv2.VideoWriter_fourcc(*'mp4v')  # You can also use other codecs like MJPG, X264, etc.
        out = cv2.VideoWriter(output_filename, codec, fps, (frame_width, frame_height), isColor=True)

        # Create background subtraction object
        backSub = cv2.createBackgroundSubtractorMOG2()

        while True:
            ret, frame = capture.read()
            if frame is None:
                break

            # Update the background model
            fgMask = backSub.apply(frame)

            # Get the frame number and write it on the current frame
            cv2.rectangle(frame, (10, 2), (100, 20), (255, 255, 255), -1)
            cv2.putText(frame, str(capture.get(cv2.CAP_PROP_POS_FRAMES)), (15, 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

            # Apply the foreground mask to the original frame
            masked_frame = cv2.bitwise_and(frame, frame, mask=fgMask)

            # Write the masked frame to the output video file
            out.write(masked_frame)

            keyboard = cv2.waitKey(30)
            if keyboard == ord('q') or keyboard == 27:
                break

        # Release video capture and writer objects
        capture.release()
        out.release()
        cmd = f"static_ffmpeg -y -i {out} -c:v libx264  -crf 34 -preset veryfast {out}.mp4"
        subprocess.run(cmd, shell=True)

def background_subtractor_absdiff(input_folder,output_folder):
    os.makedirs(output_folder, exist_ok=True)

    # Initialize video capture
    for video in os.listdir(input_folder):
        video_path = os.path.join(input_folder, video)
        capture = cv2.VideoCapture(video_path)
        success, ref_img = video.read()
        if not success:
            print("Error: Unable to read video.")
            return

        # Get the video's frame width, height, and frames per second
        frame_width = int(capture.get(3))
        frame_height = int(capture.get(4))
        fps = int(capture.get(cv2.CAP_PROP_FPS))
        video_name = Path(video).stem
        
        output_video_path = os.path.join(output_folder, video_name + "_absdiff_masked.mp4")
        video_clip = VideoFileClip(video)
        output_video = video_clip.fl_image(remove_background)
        output_video.write_videofile(output_video_path, codec='libx264', fps=fps)

    # Define a function to remove the static background from each frame
    def remove_background(frame):
        diff = cv2.absdiff(frame, ref_img)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        foreground = cv2.bitwise_and(frame, frame, mask=mask)
        return foreground
    
        



def main():
    config = ConfigHandler('reduction.background_subtractor')
    s3 = config.s3
    method = config.method
    aux = Aux()
    try:
        video_list_s3_original_video = []
        video_list_s3_original_video = aux.load_s3(
            bucket= s3['input_bucket_s3'] , prefix=method['input_prefix_s3']
        )
    except Exception as e:
        print(e)
        logging.warning(
            f"unable to load video list from s3; ensure AWS credentials have been provided."
        )
    if not os.path.exists("original_videos"):
        os.mkdir("./original_videos")
    if not os.path.exists("background_subtraction"):
        os.mkdir("./background_subtraction")
    
    
    aux.execute_label_and_write_local(video_list_s3_original_video, "original_videos")
    background_subtractor('original_videos','background_subtraction')
    background_subtractor_absdiff('original_videos','background_subtraction')
    out_video_list = os.listdir('background_subtraction')
    aux.upload_s3(out_video_list, bucket = s3['output_bucket_s3'], prefix = s3['output_prefix_s3'])

    aux.set_local_path('original_videos')
    aux.clean()
    aux.set_local_path('background_subtraction')
    aux.clean()
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))






   


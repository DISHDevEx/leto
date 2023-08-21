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
import os
import cv2
import subprocess
from pathlib import Path

def background_subtractor(input_folder, output_folder):
    ''' This code helps to extract background from the video 
    Video works usually well on the videos with static background. It will take first frame as static
    
    Parameters:
    input_folder : name of local input folder
    output_folder: name of output folder

    Returns:
    videos with background masked 
    
     '''
    
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

        # Variable to store the background image
        building_static_image(video_path, output_folder)

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
        encoded_video_name = os.path.join(output_folder, video_name + "_masked_encoded")
        cmd = f"static_ffmpeg -y -i {output_filename} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}.mp4"
        subprocess.run(cmd, shell=True)

def building_static_image(video_path, output_folder):

# Path to the video file
    video_path = video_path
    video_name = video_path.strip(".mp4")

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file")
        exit()

    # Read the first frame and convert it to grayscale for the first reference
    ret, first_frame = cap.read()
    if not ret:
        print("Error reading the first frame")
        exit()

    first_frame_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(total_frames)

    # Set the video capture to the last frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)

    # Read the last frame and convert it to grayscale for the second reference
    ret, last_frame = cap.read()
    if not ret:
        print("Error reading the last frame")
        exit()

    last_frame_gray = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)

    # Parameters for frame comparison
    static_frame = None
    static_frame_diff = float('inf')  # Initialize with a high value
    # re-initialize the frame number
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while True:
        ret, frame = cap.read()
        #print(ret)

        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        first_frame_diff = cv2.absdiff(gray_frame, first_frame_gray)
        #print(first_frame_diff)
        last_frame_diff = cv2.absdiff(gray_frame, last_frame_gray)
        #print(last_frame_diff)

        frame_diff_sum = cv2.sumElems(first_frame_diff)[0] + cv2.sumElems(last_frame_diff)[0]

        if frame_diff_sum < static_frame_diff:
            static_frame_diff = frame_diff_sum
            static_frame = frame.copy()
    #     else:
    #         static_frame_diff = min(first_frame_diff, last_frame_diff)
    #         static_frame = frame.copy()
    cap.release()

    if static_frame is not None:
        output_path = os.path.join(output_folder, video_name + ".jpg")
        cv2.imwrite(output_path, static_frame)
        print(f"Static frame saved as {output_path}")
    else:
        print("No static frame found in the video.")



def main():
    '''
      """
    Runner method for background_subtractor().  This method abstracts some of the
    interaction with S3 and AWS away from fps_bitrate.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.'''
    
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
    out_video_list = aux.load_local("./background_subtraction")
    if ".ipynb_checkpoints" in out_video_list:
        out_video_list.remove(".ipynb_checkpoints")
    aux.upload_s3(out_video_list, bucket = s3['output_bucket_s3'], prefix = method['output_prefix_s3'])

    aux.set_local_path('original_videos')
    aux.clean()
    aux.set_local_path('background_subtraction')
    aux.clean()
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))






   


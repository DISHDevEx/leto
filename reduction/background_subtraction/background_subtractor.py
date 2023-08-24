import cv2
from aEye import Aux
import logging
import os
from pathlib import Path

import subprocess
import time
import sys
import numpy as np

root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality


def background_subtractor(video_list, path="temp"):
    ''' This method helps to extract foreground from the video by removing static background
    Video works usually well on the videos with static background. 
    
    Parameters:
    input_folder : name of local input folder
    output_folder: name of output folder

    Returns:
    videos with background masked 
    
     '''
    
    # Create the output folder if it doesn't exist
    #os.makedirs(output_folder, exist_ok=True)

    # Initialize video capture
    for video in video_list:
        #video_path = os.path.join(input_folder, video)
        stream = cv2.VideoCapture(video.get_file().strip("'"))
        video_name = Path(str(video)).stem

        # Get the video's frame width, height, and frames per second
        if not stream.isOpened():
            print("No stream :(")
            exit()

        num_frames = stream.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_ids = np.random.uniform(size=20) * num_frames
        frames = []
        for fid in frame_ids:
            stream.set(cv2.CAP_PROP_POS_FRAMES, fid)
            ret, frame = stream.read()
            if not ret:
                print("SOMETHING WENT WRONG")
                exit()
            frames.append(frame)

        median = np.median(frames, axis=0).astype(np.uint8)
        median_1 = median 
        median = cv2.cvtColor(median, cv2.COLOR_BGR2GRAY)

        fps = stream.get(cv2.CAP_PROP_FPS)
        width = int(stream.get(3))
        height = int(stream.get(4))
        output_filename = os.path.join("./temp/",video_name + "_masked.mp4" )
        print(output_filename)
        output = cv2.VideoWriter(output_filename,
                                cv2.VideoWriter_fourcc(*'mp4v'),  # Change FourCC code
                                fps=fps, frameSize=(width, height), isColor=False)  # Set isColor to False

        stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, frame = stream.read()
            if not ret:
                print("No more stream :(")
                break

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff_frame = cv2.absdiff(median, frame_gray)
            #threshold, diff = cv2.threshold(diff_frame, 100, 255, cv2.THRESH_BINARY)
            output.write(diff_frame)
            #cv2.imshow("Video!", diff)

            if cv2.waitKey(1) == ord('q'):
                break

        stream.release()
        output.release() 
        cv2.destroyAllWindows()# Release the VideoWriter
        median_frame_name = os.path.join("./temp",video_name + ".jpg")
        cv2.imwrite(median_frame_name,median_1)
        encoded_video_name = os.path.join('./temp/', video_name)
        cmd = f"static_ffmpeg -y -i {output_filename} -c:v libx264  -crf 23 -preset veryfast {encoded_video_name}.mp4"
        subprocess.run(cmd, shell=True)
        

def building_static_image(video_path, output_folder):
    """This method helps to extract static frame from the video. 
    It takes first frame and last frame as reference frames and calculate abs diff from each frame 
    the frame with minumum difference is termed as static frame """

# Path to the video file
    video_path = video_path
    video_basename = os.path.basename(video_path)
    video_name = Path(video_basename).stem

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
        # building file path
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
    
    config = ConfigHandler('reduction.cv2_jpg_reduction')
    s3_args = config.s3
    method_args = config.method
    aux = Aux()

    cloud_functionality = CloudFunctionality()


    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args )
    
    
    #aux.execute_label_and_write_local(video_list_s3_original_video, "original_videos")
    background_subtractor(video_list,path="temp")
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






   


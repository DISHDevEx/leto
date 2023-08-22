# Current directory is brought to root level to avoid import issues
import subprocess
import sys

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")
# add git repo path to use all libraries
sys.path.append(root_path)

import cv2
from aEye import Aux
import logging
import os
from utilities import ConfigHandler
import configparser
from utilities import CloudFunctionality
import time



def background_addition(video_path, image_path, output_path):
    """This methods adds static background to masked image
    Parameters
    Videopath: path to image 
    Imagepath: static background

    Returns:
    Reconstructed videos with background added
    
    """
    cap = cv2.VideoCapture(video_path)
    
    image = cv2.imread(image_path)

    # Get the dimensions of the video frames
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create a VideoWriter object to save the output
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_path, fourcc, 30, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize the image to match the video frame size
        resized_image = cv2.resize(image, (frame_width, frame_height))
        
        # Combine the image and video frames
        combined_frame = cv2.addWeighted(frame, 1, resized_image, 0.5, 0)

        out.write(combined_frame)
   
    cap.release()
    
    out.release()
    
    vname = output_path.split('/')[1]    
    name = vname.strip('.mp4')
    output_folder = output_path.split('/')[0]
    encoded_video_name = os.path.join(output_folder, name + '_background.mp4')
    
    cmd = f"static_ffmpeg -y -i {output_path} -c:v libx264 -crf 34 -preset veryfast {encoded_video_name}"
    subprocess.run(cmd, shell=True)
    
    os.remove(output_path)

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
    
    cloud_functionality = CloudFunctionality()

    # load and allocate config file
    config = ConfigHandler('reconstruction.background_addition')
    s3_args = config.s3
    method_args = config.method
    

    cloud_functionality.preprocess(method_args, s3_args)
    
    folder_path = 'reduced_videos'

    videos = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    images = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

    matched_files = []
    

    for video in videos:
        video_filename = os.path.splitext(video)[0]
        matching_img = f"{video_filename}.jpg"
        
        if matching_img in images:
            video_path = os.path.join(folder_path, video)
            image_path = os.path.join(folder_path, matching_img)
            matched_files.append((video_path, image_path))
        

    for files in matched_files:
 
        name = files[0].split('/')[1]
        background_addition(files[0],files[1],f'reconstructed_videos/{name}')
  
    cloud_functionality.postprocess(method_args, s3_args)
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
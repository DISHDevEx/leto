import cv2
from aEye import Aux
import logging
import os
from utilities import ConfigHandler

import configparser
from utilities import CloudFunctionality


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
    output_path = output_path
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

        cv2.imshow('Combined Video', combined_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


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
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    config.read('../../config.ini')
    s3_args = config['DEFAULT']
    method_args = config['reconstruction.recon_args']
    logging.info("successfully loaded config file")

    cloud_functionality.preprocess(method_args, s3_args)

    videos = [f for f in os.listdir('reduced_videos') if f.endswith('.mp4')]
    images = [f for f in os.listdir('reduced_videos') if f.endswith('.jpg')]

    matched_files = []

    for video in videos:
        video_filename = os.path.splitext(video)[0]
        matching_img = f"{video_filename}.jpg"
        if matching_img in images:
            matched_files.append((video_filename, matching_img))
        
    
    for files in matched_files:
        background_addition(files[0],files[1],'reconstructed_videos')
  
    cloud_functionality.postprocess(method_args, s3_args)
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))




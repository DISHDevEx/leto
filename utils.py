import cv2
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim
from aEye.auxiliary import Aux
import os
import re


class Evaluator:
    def __init__(self):
        print("Start calculating Video metrics") 


    def calculate_psnr(self,original_path, compressed_path):
        '''
        This will help to calculate PSNR for video having any resolution 
            PSNR is Peak Signal to Noise ratio  which is used o measure the quality of a reconstructed or compressed image or video signal 
            compared to its original, uncompressed version. 
            It provides a quantitative measure of the fidelity of 
            the reconstructed signal by calculating the ratio 
            between the maximum possible signal power (peak signal) 
            and the power of the distortion or noise introduced 
            during the compression or reconstruction process.
          Parameters
        ----------------------
            original_video: Video file in any format(mp4, avi etc)
            compressed_video : Video file after reduction/ reconstruction (mp4, avi etc)

         Returns
         ----------
        average_psnr : float
            It gives Peak to signal ratio between 2 videos
             range :Excellent: Above 40 dB
                    Good: 30 to 40 dB
                    Fair: 20 to 30 dB
                    Poor: Below 20 dB
        '''
    # Read videos
        original_video = cv2.VideoCapture(original_path)
        compressed_video = cv2.VideoCapture(compressed_path)




        # Get video properties
        num_frames = min(int(original_video.get(cv2.CAP_PROP_FRAME_COUNT)), int(compressed_video.get(cv2.CAP_PROP_FRAME_COUNT)))
        fps = int(original_video.get(cv2.CAP_PROP_FPS))

        # Initialize PSNR value
        total_psnr = 0.0

        for _ in range(num_frames):
            # Read frames
            ret1, frame1 = original_video.read()
            ret2, frame2 = compressed_video.read()

            # Resize compressed frame to match the resolution of the original frame
            frame2_resized = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]), interpolation=cv2.INTER_LINEAR)

            # Convert frames to floating-point format for PSNR calculation
            frame1 = frame1.astype(np.float64)
            frame2_resized = frame2_resized.astype(np.float64)

            # Calculate MSE (Mean Squared Error)
            mse = np.mean((frame1 - frame2_resized) ** 2)

            # Calculate PSNR
            if mse == 0:
                # PSNR is infinite when MSE is 0, in this case, PSNR = 100
                psnr = 100.0
            else:
                max_pixel = 255.0
                psnr = 20 * np.log10(max_pixel / np.sqrt(mse))

            # Accumulate PSNR value
            total_psnr += psnr

        # Calculate average PSNR
        average_psnr = total_psnr / num_frames

        # Release video objects
        original_video.release()
        compressed_video.release()

        return average_psnr

    def calculate_video_ssim(self,original_path, compressed_path):
        '''This works with video of any resolution
           SSIM is is a perceptual metric that quantifies image quality 
           degradation* caused by processing such as data compression or by losses in data transmission. 
           It is a full reference metric that requires two images 
           from the same image capture— a reference image and a processed image


           Parameters
        ----------------------
            original_video: Video file in any format(mp4, avi etc)
            compressed_video : Video file after reduction/ reconstruction (mp4, avi etc)

         Returns
    ----------
        average_ssim : float
            It gives structural similarity value between 2 videos
             range : -1 to +1
             -1 -> no similarity
             +1 -> perfect similarity
  
    
        '''
        original_video = cv2.VideoCapture(original_path)
        compressed_video = cv2.VideoCapture(compressed_path)

        # Get video properties
        num_frames = min(int(original_video.get(cv2.CAP_PROP_FRAME_COUNT)), int(compressed_video.get(cv2.CAP_PROP_FRAME_COUNT)))
        fps = int(original_video.get(cv2.CAP_PROP_FPS))

        # Initialize SSIM value
        total_ssim = 0.0

        for _ in range(num_frames):
            # Read frames
            ret1, frame1 = original_video.read()
            ret2, frame2 = compressed_video.read()

            # Resize compressed frame to match the resolution of the original frame
            frame2_resized = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]), interpolation=cv2.INTER_LINEAR)

            # Convert frames to grayscale for SSIM calculation
            gray_frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray_frame2 = cv2.cvtColor(frame2_resized, cv2.COLOR_BGR2GRAY)

            # Calculate SSIM
            ssim = compare_ssim(gray_frame1, gray_frame2)

            # Accumulate SSIM value
            total_ssim += ssim

        # Calculate average SSIM
        average_ssim = total_ssim / num_frames

        # Release video objects
        original_video.release()
        compressed_video.release()

        return average_ssim

    def read_max_files_s3(self,bucket_name,prefix_orginal_file, prefix_reduced_file):
        ''' Function to read file from S3 using aEye 
        Parameters:
        bucket_name = S3 bucket name
        prefix_orginal_file : path where original buckets are stored
        prefix_reduced_file : path where reduced buckets are stored
        
        Returns:
        after matching return orginal 
        video file path and reduced video file path of same video
        '''

        aux = Aux()
        # read files from S3 in a list
        video_list_s3_original_video = aux.load_s3(bucket = bucket_name, prefix = prefix_orginal_file)
        video_list_s3_reduced_video = aux.load_s3(bucket = bucket_name, prefix = prefix_reduced_file)
        # make directories to store files locally
        if not os.path.exists('original_videos'):
            os.mkdir('./original_videos')
        if not os.path.exists('reduced_videos'):
            os.mkdir('./reduced_videos')
        # load videos to local
        aux.execute_label_and_write_local(video_list_s3_original_video, 'original_videos')
        aux.execute_label_and_write_local(video_list_s3_reduced_video, 'reduced_videos')
         
         # Match file names 
        for i in range(len(os.listdir('original_videos'))):
            original_video_path = os.path.join('./original_videos/',os.listdir('original_videos')[i])
            original_video_name = os.listdir('original_videos')[i].split(".")[0].lower()
            for file_name in os.listdir('reduced_videos'):
                if original_video_name in file_name:
                    reduced_video_path = os.path.join('./reduced_videos/',file_name)
                    return original_video_path, reduced_video_path
                else:
                        return ("Videos are different")



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

    def read_files_and_store_locally(self,bucket_name,prefix_orginal_files, prefix_reduced_files):
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
        video_list_s3_original_video = aux.load_s3(bucket = bucket_name, prefix = prefix_orginal_files)
        video_list_s3_reduced_video = aux.load_s3(bucket = bucket_name, prefix = prefix_reduced_files)
        # make directories to store files locally
        if not os.path.exists('original_videos'):
            os.mkdir('./original_videos')
        if not os.path.exists('reduced_videos'):
            os.mkdir('./modified_videos')
        # load videos to local
        aux.execute_label_and_write_local(video_list_s3_original_video, 'original_videos')
        aux.execute_label_and_write_local(video_list_s3_reduced_video, 'modified_videos')
        return ("Files have been successfully loaded")


    def match_files(self,original_folder, modified_folder):
        ''' Function to match original video to reduced/reconstructed video
            Parameters:
            original_folder :str name of original_folder location
            modified_folder : str original folder location

            Return:
            video_path_pair_list : list -> consisting of tuple between original_video_path and reduced filepath
        '''
         # Match file names 
        video_path_pair_list = []
        for i in range(len(os.listdir(original_folder))):
            original_video_path = os.path.join(original_folder,os.listdir(original_folder)[i])
            original_video_name = os.listdir(original_folder)[i].split(".")[0].lower()
            for file_name in os.listdir(modified_folder):
                file_name_1 = file_name.lower()
                if original_video_name in file_name_1:
                    reduced_video_path = os.path.join(modified_folder ,file_name)
                    video_tuple = (original_video_path,reduced_video_path)
                    video_path_pair_list.append(video_tuple)
        if len(video_path_pair_list) ==0:
            return("No videos match")
        else:
            return video_path_pair_list
    

    def create_scores_dict(self,video_path_list):
        '''
        Function gives list of dictionaries with ssim and PSNR calculated 
        Parameters:
        video_path_list = list of tuple of pair of original and reconstructed/reduced videos

        Returns:
        list_scores : a list of dictionaries containing scores
        
        
        '''
        list_scores =[]
        video_val = Evaluator()
        for i in range(0,len(video_path_list)):
            dict_1 ={}
            original_file_path = video_path_list[i][0]
            reconstructed_file_path = video_path_list[i][1]
            psnr_score = video_val.calculate_psnr(original_file_path, reconstructed_file_path)
            print(f"Video PSNR: {psnr_score} dB")
            ssim_score = video_val.calculate_video_ssim(original_file_path, reconstructed_file_path)
            dict_1['original_file_path']  = video_path_list[i][0]
            dict_1['reconstructed_file_path']  = video_path_list[i][1]
            dict_1["psnr"] = psnr_score
            dict_1["ssim"] = ssim_score
            print(dict_1)
            list_scores.append(dict_1)
        return list_scores


    def clean_files(self,path_to_orginal_folder, path_to_modified_folder):
        # delete local files
        aux = Aux()
        aux.set_local_path(path_to_orginal_folder)
        aux.clean()
        aux.set_local_path(path_to_modified_folder)
        aux.clean()
        return print("Folders removed")



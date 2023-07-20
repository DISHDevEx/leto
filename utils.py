import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

class Evaluator:
    def __init__(self):
        print("Start calcuting Video metrics") 
    
    def calculate_psnr(self,original_video, compressed_video):
        ''' This will help to calculate PSNR for video having same resolution 
            PSNR is Peak Signal to Noise ratio  which is used o measure the quality of a reconstructed or compressed image or video signal 
            compared to its original, uncompressed version. 
            It provides a quantitative measure of the fidelity of 
            the reconstructed signal by calculating the ratio 
            between the maximum possible signal power (peak signal) 
            and the power of the distortion or noise introduced 
            during the compression or reconstruction process. '''
        input_cap = cv2.VideoCapture(original_video)
        output_cap = cv2.VideoCapture(compressed_video)

        frame_count = min(int(input_cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(output_cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        total_psnr = 0

        for _ in range(frame_count):
            ret1, input_frame = input_cap.read()
            ret2, output_frame = output_cap.read()

            if not ret1 or not ret2:
                break

            psnr = Evaluator.calculate_psnr_frame(input_frame, output_frame)
            total_psnr += psnr

        input_cap.release()
        output_cap.release()

        mean_psnr = total_psnr / frame_count
        return mean_psnr

    def calculate_psnr_frame(original_frame, compressed_frame):
        ''' This is the helper function to calculate frame by frame'''
        mse = np.mean((original_frame - compressed_frame) ** 2)
        max_pixel_value = np.max(original_frame)
        psnr = 10 * np.log10((max_pixel_value ** 2) / mse)
        return psnr

    def calculate_video_ssim(self,input_file, output_file):
        '''This also works with video of same resolution'''
        input_cap = cv2.VideoCapture(input_file)
        output_cap = cv2.VideoCapture(output_file)

        ssim_values = []
        frame_count = min(int(input_cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(output_cap.get(cv2.CAP_PROP_FRAME_COUNT)))

        for _ in range(frame_count):
            ret1, input_frame = input_cap.read()
            ret2, output_frame = output_cap.read()

            if not ret1 or not ret2:
                break

            input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY)
            output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2GRAY)

            ssim_value = ssim(input_frame, output_frame)
            ssim_values.append(ssim_value)

        input_cap.release()
        output_cap.release()

        mean_ssim = np.mean(ssim_values)
        return mean_ssim

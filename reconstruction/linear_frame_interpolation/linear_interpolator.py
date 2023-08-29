import cv2
import os
import subprocess
from pathlib import Path

def linear_interpolation(frame_a, frame_b, alpha):
    return cv2.addWeighted(frame_a, 1 - alpha, frame_b, alpha, 0)

def reconstruct_video_with_keyframe_images(video_list, target_frame_rate= 30, path="temp"):
        for video in video_list:
            video_path = video.get_file().strip("'")
            cap = cv2.VideoCapture(video_path)
            video_name = Path(str(video)).stem


            # Get video properties
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            input_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            num_interpolated_frames = (target_frame_rate /frame_rate) -1


            # Create VideoWriter to save interpolated video
            output_filename = os.path.join(path,video + "_interpolated.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 video
            out = cv2.VideoWriter(output_filename, fourcc, output_frame_rate, frame_size)

            # Read frames and perform interpolation
            ret, frame_a = cap.read()
            while ret:
                ret, frame_b = cap.read()

                if not ret:
                    break

                # Perform linear interpolation
                for i in range(num_interpolated_frames + 1):
                    alpha = i / (num_interpolated_frames + 1)
                    interpolated_frame = linear_interpolation(frame_a, frame_b, alpha)
                    out.write(interpolated_frame)

                frame_a = frame_b
            out.write(frame_b)

            # Release VideoCapture and VideoWriter
            cap.release()
            out.release()
            encoded_video_name = os.path.join(path,video + ".mp4")
            cmd = f"static_ffmpeg -y -i {output_filename} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}.mp4"
            subprocess.run(cmd, shell=True)
            os.remove(output_filename)


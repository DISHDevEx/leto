import os
import cv2
from aEye import Aux
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
import numpy as np
from sklearn.cluster import KMeans
import time
import boto3
from pathlib import Path
import subprocess

root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler
from utilities import CloudFunctionality


# Load the model
cnn_model = resnet50(pretrained=True)
cnn_model = cnn_model.eval()


def extract_frame_features(frame):
    """
        Extracts deep features from an input image frame using a pre-trained CNN model.

        This function takes an image frame as input, preprocesses it by applying transformations
        including resizing and normalization, and then extracts deep features from the image using
        a pre-trained Convolutional Neural Network (CNN) model. The extracted features are flattened
        and returned as a NumPy array.

        Parameters:
        ----------
            frame (PIL.Image or Tensor): The input image frame to extract features from.

        Returns:
        ----------
            numpy.ndarray: A 1-dimensional NumPy array containing the flattened deep features
                extracted from the input image frame."""
    transform = transforms.Compose(
        [
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    frame = transform(frame)
    frame = torch.unsqueeze(frame, 0)

    # Extract features using the CNN model
    with torch.no_grad():
        features = cnn_model(frame)

    return features.flatten().numpy()


def extract_key_frames(video_list, path="temp", num_key_frames=30):
    """
    Extracts and generates key frames from a list of input videos using K-Means clustering.

    This function takes a list of video filenames, processes each video to extract frame features,
    performs K-Means clustering to select representative key frames, and then generates a new video
    containing the selected key frames. The generated video is further compressed using FFmpeg.

    Parameters:
    ----------
        video_list (list): A list of video filenames to process and generate key frames from.
        path (str, optional): The directory path where the generated videos will be saved. Default is "temp".
        num_key_frames (int, optional): The number of key frames to select for each video. Default is 30.

    Returns:
    ----------
        None
        """

    for video in video_list:
        video_path = os.path.join(video.get_file().strip("'"))
        cap = cv2.VideoCapture(video_path)
        video_name = Path(video_path).stem
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        # duration_seconds = frame_count / frame_rate
        target_fps = int(num_key_frames / 10)
        frames = []

        # Extract features from each frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(extract_frame_features(frame))

        cap.release()

        # Apply K-Means clustering and select key frames
        kmeans = KMeans(n_clusters=num_key_frames, random_state=0)
        kmeans.fit(frames)
        cluster_centers = kmeans.cluster_centers_

        # Calculate the distance of each frame to the cluster centers
        distances = np.linalg.norm(
            np.array(frames)[:, np.newaxis] - cluster_centers, axis=2
        )
        # Get the index of the closest cluster center for each frame
        closest_clusters = np.argmin(distances, axis=1)

        # Get one representative key frame from each cluster
        key_frames = []
        for cluster_idx in range(num_key_frames):
            cluster_frames = np.where(closest_clusters == cluster_idx)[0]
            representative_frame_idx = cluster_frames[
                np.argmax(distances[cluster_frames, cluster_idx])
            ]
            key_frames.append(representative_frame_idx)

        # make video from frames
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = os.path.join(path, video_name + "_keyframes.mp4")
        out = cv2.VideoWriter(
            output_path, fourcc, target_fps, (frame_width, frame_height), isColor=True
        )
        video_stream = cv2.VideoCapture(video_path)
        key_frames.sort()
        for i in key_frames:
            video_stream.set(cv2.CAP_PROP_POS_FRAMES, i)

            ret, frame = video_stream.read()
            if not ret:
                return
            out.write(frame)
        video_stream.release()
        out.release()
        encoded_video_name = os.path.join(path, video_name + ".mp4")
        cmd = f"static_ffmpeg -y -i {output_path} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}"
        subprocess.run(cmd, shell=True)
        os.remove(output_path)


def main():
    """
    Runner method for keyframe_extraction().  This method abstracts some of the
    interaction with S3 and AWS away from fps_bitrate.

    Parameters
    ----------
        None: runner method


    Returns
    ----------
        None: however, results in a list of processed videos being stored to the
                output video S3 path.'''
    
    """
    config = ConfigHandler("reduction.keyframe_extraction")
    s3_args = config.s3
    method_args = config.method

    cloud_functionality = CloudFunctionality()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)
    extract_key_frames(
        video_list, method_args["temp_path"], method_args.getint("num_key_frames")
    )
    cloud_functionality.postprocess_reduction(s3_args, method_args)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

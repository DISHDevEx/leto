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
    
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    frame = transform(frame)
    frame = torch.unsqueeze(frame, 0)

    # Extract features using the CNN model
    with torch.no_grad():
        features = cnn_model(frame)

    return features.flatten().numpy()

def extract_key_frames_indices(video_list, num_key_frames=30 , path = 'temp'):
     for video in video_list:
        video_path = video.get_file().strip("'")
        stream = cv2.VideoCapture(video.get_file().strip("'"))
        if not stream.isOpened():
            exit()
        video_name = Path(str(video)).stem
        frame_count = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []

        # Extract features from each frame
        for _ in range(frame_count):
            ret, frame = stream.read()
            if not ret:
                break
            frames.append(extract_frame_features(frame))

        stream.release()

        # Apply K-Means clustering and select key frames
        kmeans = KMeans(n_clusters=num_key_frames, random_state=0)
        kmeans.fit(frames)
        cluster_centers = kmeans.cluster_centers_

        # Calculate the distance of each frame to the cluster centers
        distances = np.linalg.norm(np.array(frames)[:, np.newaxis] - cluster_centers, axis=2)
        # Get the index of the closest cluster center for each frame
        closest_clusters = np.argmin(distances, axis=1)

        # Get one representative key frame from each cluster
        key_frames = []
        for cluster_idx in range(num_key_frames):
            cluster_frames = np.where(closest_clusters == cluster_idx)[0]
            representative_frame_idx = cluster_frames[np.argmax(distances[cluster_frames, cluster_idx])]
            key_frames.append(representative_frame_idx)
        # save keyframes
        output_keyframe_path = os.path.join(path,video_name+ "_")
        save_key_frames(video_path,key_frames, output_keyframe_path )


        return print("keyframes extract at {}".path)


def save_key_frames(video_path, key_frames_indices, output_keyframe_path):
    if not os.path.exists(path):
        os.makedirs(path)

    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    key_frame_counter = 0

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        if i in key_frames_indices:
            key_frame_path = os.path.join(output_keyframe_path, f"key_frame_{key_frame_counter}.jpg")
            cv2.imwrite(key_frame_path, frame)
            key_frame_counter += 1

    cap.release()

def generate_keyframe_video(input_image_list,fps, frame_size, output_video_path):
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Change the codec as needed
    
    output_video = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)
    for image in input_image_list:
        image_path = os.path.join(output_video_path, image)
        frame = cv2.imread(image_path)
        output_video.write(frame)
    
# Release the VideoWriter and close all windows
    output_video.release()
    cv2.destroyAllWindows()
    encoded_video_name = os.path.join(output_video_path, "_encoded.mp4")
    cmd = f"static_ffmpeg -y -i {output_video_path} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}"
    subprocess.run(cmd, shell=True)




def upload_keyframes_to_S3(bucket_name,s3_folder_prefix,local_folder_path):
    s3 = boto3.resource('s3')
    bucket_name = bucket_name
    s3_folder_prefix = s3_folder_prefix
    local_folder_path = local_folder_path

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            
            s3_key = s3_folder_prefix + os.path.basename(local_file_path)
            print(s3_key)
            s3_object = s3.Object(bucket_name, s3_key)
            s3_object.upload_file(local_file_path)


def main():
    config = ConfigHandler("reduction.background_subtractor")
    s3_args = config.s3
    method_args = config.method
    aux = Aux()

    cloud_functionality = CloudFunctionality()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)
    extract_key_frames_indices(video_list ,num_key_frames=30 , path = 'temp')


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
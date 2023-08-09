import os
import cv2
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
import numpy as np
from sklearn.cluster import KMeans
import time
import boto3
import argparse


# Load the model 
cnn_model = resnet50(pretrained=True)
cnn_model = cnn_model.eval()

def parse_args():
    """
    Parses the arguments needed for keyframe extraction reduction module.
    Catalogues: input s3 bucket, input s3 prefix, output s3 bucket and output s3 prefix.


    Returns
    -------
        args: argparse.Namespace object
            Returns an object with the relevent input s3 bucket, input s3 prefix, output s3 bucket and output s3 prefix, fps, and bitrate.
    """

    parser = argparse.ArgumentParser(
        description="Inference script of ffmpeg resolution downsampler"
    )
    parser.add_argument(
        "--input_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the input video",
    )

    parser.add_argument(
        "--input_prefix_s3",
        type=str,
        default="original-videos/benchmark/car/",
        help="s3 prefix of the input video",
    )

    parser.add_argument(
        "--output_bucket_s3",
        type=str,
        default="leto-dish",
        help="s3 bucket of the input video",
    )

    parser.add_argument(
        "--output_prefix_s3",
        type=str,
        default="reduced-videos/benchmark/keyframe-extraction/car/",
        help="s3 prefix of the output video",
    )

    args = parser.parse_args()

    return args


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

def extract_key_frames(video_path, num_key_frames=10):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []

    # Extract features from each frame
    for _ in range(frame_count):
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
    distances = np.linalg.norm(np.array(frames)[:, np.newaxis] - cluster_centers, axis=2)
    # Get the index of the closest cluster center for each frame
    closest_clusters = np.argmin(distances, axis=1)

    # Get one representative key frame from each cluster
    key_frames = []
    for cluster_idx in range(num_key_frames):
        cluster_frames = np.where(closest_clusters == cluster_idx)[0]
        representative_frame_idx = cluster_frames[np.argmax(distances[cluster_frames, cluster_idx])]
        key_frames.append(representative_frame_idx)

    return key_frames


def save_key_frames(video_path, key_frames_indices, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    key_frame_counter = 0

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        if i in key_frames_indices:
            key_frame_path = os.path.join(output_folder, f"key_frame_{key_frame_counter}.jpg")
            cv2.imwrite(key_frame_path, frame)
            key_frame_counter += 1

    cap.release()

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
    args = parse_args()
    video_path = "collision00.mp4"
    key_frames_indices = extract_key_frames(video_path)

    output_folder = "keyframe_cnn_collission"

    save_key_frames(video_path, key_frames_indices, output_folder)

    return print(f"{len(key_frames_indices)} key frames saved to {output_folder}.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
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

def extract_key_frames(video_list, path ='temp', num_key_frames=30):
    for video in video_list:
        video_path = os.path.join('/root/PyTorchVideoCompression/original_videos/',video)
        cap = cv2.VideoCapture(video_path)
        video_name = Path(video_path).stem
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(frame_count/num_key_frames)
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

         # make video from frames 
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = os.path.join(path, video_name+'_keyframes.mp4')
        print(output_path)
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height), isColor=True)
        video_stream = cv2.VideoCapture(video_path)
        key_frames.sort()
        #print(key_frames)
        for i in key_frames:
            #print(i)
            video_stream.set(cv2.CAP_PROP_POS_FRAMES, i)

            ret, frame = video_stream.read()
            if not ret:
                print("Failed to read target frame.")
                return
            out.write(frame)
        video_stream.release()
        out.release()
        encoded_video_name = os.path.join(path, video_name+'.mp4')
        cmd = f"static_ffmpeg -y -i {output_path} -c:v libx264  -crf 34 -preset veryfast {encoded_video_name}"
        subprocess.run(cmd, shell=True)
        os.remove(output_path)

        
    




def main():
    config = ConfigHandler("reduction.background_subtractor")
    s3_args = config.s3
    method_args = config.method

    cloud_functionality = CloudFunctionality()

    video_list = cloud_functionality.preprocess_reduction(s3_args, method_args)
    extract_key_frames(video_list ,method_args["temp_path"], method_args.getint('num_key_frames') )
    cloud_functionality.postprocess_reduction(s3_args, method_args)


    


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
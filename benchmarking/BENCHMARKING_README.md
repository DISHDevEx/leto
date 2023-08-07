# Yolo Model

Please read the Yolo model readme for more instructions.

# Mediapipe Model

Please read the Mediapipe model readme for more instructions.

# Evaluating metrics

## Running utils file


1. Move to working directory
```console
cd utilities
```

2. Run requirements_utilities.txt
```
pip install -r requirements_utilities.txt
```

3. Run the following command to import Evaluator class and Get PSNR and SSIM
```
from utils import *
```
## if checking locally
```
original_file_path = 'path/to/input/file'
reconstructed_file_path = 'path/to/output/file' ( Add your orginal and recontructed file)
```
## Call calculate_psnr and calculate ssim metrics
```
psnr = calculate_psnr(original_file_path, reconstructed_file_path)
print(f"Video PSNR: {psnr} dB")

ssim = calculate_video_ssim(original_file_path, reconstructed_file_path)
print(f"SSIM: {ssim}")
```


## for calculating PSNR and SSIM for videos in S3 bucket.
1. First load the videos from s3 to local
 ```
read_files_and_store_locally(bucket_name, prefix_to_original_file, prefix_reduced_file)

```

2. call the function (video_eval.match_files) to get a  list of tuple of type  - (original_file_path,modified_file_path). Input will be  local_folders names created in above step (eg: 'original_videos', 'modified_videos')

```
video_path_list  = match_files('original_videos', 'modified_videos')

```

3. Getting result scores in a form of list of dictionaries

```
list_scores = create_scores_dict(video_path_list)


```

4. cleanup  local filesi

```
clean_files(path_to_orginal_folder,path_to_modified_folder)
```

## Average Precision
The average precision is computed as the benchmarking model detects the objects in the video.
Ensure the working directory is the root directory

1. Install the requirements for one of the benchmarking model.
```console
#YOLO
!pip install -r benchmarking/yolo/requirements_yolo.txt
#Mediapipe
!pip install -r benchmarking/mediapipe_model/requirements_mp.txt
```

2. Import the required utility
```console
import boto3
import cv2
from aEye import Video
from aEye import Aux
from benchmarking.yolo import Yolo
from utilities import *
```

3. Import videos using aux object
```console
aux = Aux()
video_list_s3 = aux.load_s3(bucket = 'leto-dish', prefix = 'original-videos/benchmark/collisiondetection/')
```

4. Load in benchmarking model

```console
model = Yolo()
model.load_model_weight('yolov8s.pt')  #this model .pt is a pretrained model from yolov8 to detect 80 objects . Other models are found in S3
```
#mediapipe
Download the pretrained mediapipe model
https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/latest/efficientdet_lite0.tflite

store this file path into a variable 'model'.

5. Compute Average Confidence
```
average_confidence = []
for video in video_list_s3:
  #yolo
  average_confidence.append(calculateMAC_yolo(video,model))
  #mediapipe
  average_confidence.append(calculateMAC_mp(video,model))
```
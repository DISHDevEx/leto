# **Leto**
----------------------------------
# Project Structure

```
├──  leto				contains all modules that facilites all functionality to achieve leto's goal
│   ├── downstream_model
│       ├── mediapipe
│           ├── object_detection.py
│           ├── visualize.py
│           ├── Dockerfile_mp
│           ├── requirements_mp.txt
│           ├── Dockerfile_mp
│           ├──lambda_function_mp.py
│       ├── yolo
│           ├── yolo.py
│           ├── pipeline.py
│           ├── training_parameter_input.py
│           ├── prediction_parameter_input.py
│           ├── pipeline.py
│           ├── visualize.py
│           ├── Dockerfile_yolo
│           ├──lambda_function_yolo.py
│           ├── requirements_yolo.txt
│   ├── reduction
│       ├── ffmpeg_resolution_downsampler
│           ├── requirements_ffmpeg_resolution_downsampler.txt
│           ├── ffmpeg_resolution_downsampler.py
│       ├── fps_bitrate
│           ├── fps_bitrate.py
│           ├── app-fps_bitrate.py
│           ├── requirements.txt
│           ├── README.md
│
│   ├── reconstruction
│       ├── realbasicvser
│           ├── builder.py
│           ├── realbasicvsr_x4.py
│           ├── realbasicvsr_x4.py
│           ├── reconstruction_realbasicvsr_setup.sh
│           ├── realbasicvsr_preprocessing.py
│           ├── reconstruction_realbasicvsr.py
│           ├── realbasicvsr_postprocessing.py
│       ├── opencv_resoltion_upscaler
│           ├── requirements_opencv_resoltion_upscaler.txt
│           ├── opencv_resoltion_upscaler.py
│       ├── superres
│           ├── requirements_superres.txt
│           ├── reconstruction_superres.py
│   ├── utilities
|       ├──download_model.py
|       ├──metrics.py
|
│
├──  tests				contains unit tests
│   ├── test_get_meta_data.py
│   ├── conftest.py
│   ├── test_data
│      ├── test_video.mp4

```
----------------------------------
# Reduction Modules
- ffmpeg_resolution_downsampler
- View the [fps_bitrate README](/reduction/fps_bitrate/README.md) for run-book


### Running ffmpeg resolution downsampler

1. Move to working directory
```console
cd leto/reduction/ffmpeg_resolution_downsampler
```

2. Pip install requirements
```console
pip install -r requirements_ffmpeg_resolution_downsampler.txt
```

3. Run the python file
```console
python ffmpeg_resolution_downsampler.py
```

* debugging note: if you get a ImportError: libGL.so.1, run the following
```console
  apt-get update && apt-get install libgl1
```

Default input: s3://leto-dish/original-videos/benchmark/car/
Default output: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/


----------------------------------
# Reconstruction Modules

- RealBasicVSR

### Running RealBasicVSR

1. Move to working directory
```console
cd ~/leto/reconstruction/realbasicvsr
```

2. Run requirements_superres_setup.sh to install dependencies
```console
bash reconstruction_realbasicvsr_setup.sh
```
- Ensure base is activated for packages to install in path {sagemaker}.

3. Run preprocessing function
```console
python realbasicvsr_preprocessing.py
```
- Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/

- Note Pre Processing will save local video and a 200mb pretrained model

4. Run inference module on desired vido
```console
python reconstruction_realbasicvsr.py {input_dir} {output_dir}
```
Example:
```console
python reconstruction_realbasicvsr.py  ./reduced_videos/resized_480x360_video_benchmark_car.mp4 ./reconstructed_videos/reconstructed_4x_video_benchmark_car.mp4
```

-  Necessary arguments: input_dir, output_dir

5. Run postprocessing function
```console
python realbasicvsr_postprocessing.py
```
- Default cloud output: s3://leto-dish/reconstructed-videos/benchmark/realbasicvsr/car/

- Optional argument to delete locally saved pretrained model (from preprocessing).
- Note Postprocessor will delete any locally saved video**

- OpenCV Resolution Upscaler

### Running opencv resolution upscaler

1. Move to working directory
```console
cd reconstruction/opencv_resolution_upscaler
```

2. Pip install requirements
```console
pip install -r requirements_opencv_resolution_upscaler.txt
```

3. Run the python file
```console
python opencv_resolution_upscaler.py
```

* debugging note: if you get a ImportError: libGL.so.1, run the following
```console
  apt-get update && apt-get install libgl1
```

Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4

Default cloud output: s3://leto-dish/reconstructed-videos/benchmark/opencv/car/video_benchmark_car_upscaled.mp4

- SuperResolution

### Running SuperResolution

1. Move to working directory
```console
cd reconstruction/superres
```

2. Run requirements_superres_setup.sh to install dependencies
```console
bash requirements_superres_setup.sh
```

3. Run the python file
```console
python reconstruction_superres.py
```
- Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4
- Default cloud outout: s3://leto-dish/reconstructed-videos/benchmark/super_res/car/benchmark_superres_fsrcnn.mp4
- This file will delete locally saved video file and pre-trained model

### Yolo Model

Please read the Yolo model readme for more instructions.

### Mediapipe Model

Please read the Mediapipe model readme for more instructions.

# Evaluating metrics

## Average Precision
The average precision is computed as the downstream model detects the objects in the video. 
Ensure the working directory is the root directory

1. Install the requirements for one of the downstream model.
```console
#YOLO
!pip install -r downstream_model/yolo/requirements_yolo.txt
#Mediapipe
!pip install -r downstream_model/mediapipe_model/requirements_mp.txt
```

2. Import the required utility
```console
import boto3
import cv2
from aEye import Video
from aEye import Aux
from downstream_model.yolo import Yolo
from utilities import *
```

3. Import videos using aux object
```console
aux = Aux()
video_list_s3 = aux.load_s3(bucket = 'leto-dish', prefix = 'original-videos/benchmark/collisiondetection/')
```

4. Load in Downstream model

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

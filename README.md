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
│       ├── fastsrgan
│           ├── fastsrgan.py
│           ├── requirements_fastsrgan.txt
|
│   ├── utilities
|       ├──cloud_functionality.py
|       ├──recon_args.py
|       ├──utils.py
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

Default input: s3://leto-dish/original-videos/benchmark/car/
Default output: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/

### Running fps_bitrate reduction

1. Move to working directory:
```console
cd leto/reduction/fps_bitrate
```

3. Install requirements:

```console
pip install -r requirements_fps_bitrate.txt
```

4. Execute the runner method, ***app_fps_bitrate.py***

```console
python app_fps_bitrate.py
```


----------------------------------
# Reconstruction Modules

- Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4

- Default cloud outout: s3://leto-dish/reconstructed-videos/benchmark/misc/car/resized_480x360_video_benchmark_car.mp4

### Running RealBasicVSR

- **Very High Quality SR, takes a very LONG time**
- **Reccomended EC2 Image image-id ami-051619310404cab17**

1. Move to working directory
```console
cd ~/leto/reconstruction/realbasicvsr
```

2. Run requirements_superres_setup.sh to install dependencies
```console
bash reconstruction_realbasicvsr_setup.sh
```

3. Run the python file
```console
python reconstruction_realbasicvsr.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --download_model {True}{False} \
 --clean_model {True}{False} \
 --model_prefix_s3 pretrained-models/realbasicvsr_x4.pth
 --local_model_path realbasicvsr_x4.pth
```
ex/
```console
python reconstruction_realbasicvsr.py \
--output_prefix_s3 reconstructed-videos/benchmark/realbasicvsr/car/ \
--model_prefix_s3 pretrained-models/realbasicvsr_x4.pth \
--local_model_path realbasicvsr_x4.pth
--clean_model True
```



### Running opencv resolution upscaler

1. Move to working directory
```console
cd reconstruction/opencv_resolution_upscaler
```

2. Install dependencies
```python
pip install -r requirements_opencv_resolution_upscaler.txt
```

3. Run the python file
```console
python opencv_resolution_upscaler.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --resolution{} \
 --download_model False \
 --clean_model False \
```
ex/
```console
python opencv_resolution_upscaler.py \
--output_prefix_s3 reconstructed-videos/benchmark/opencv/car/ \
--resolution 1920 1080 \
--download_model False \
--clean_model False \
```

### Running SuperResolution

1. Move to working directory
```console
cd reconstruction/superres
```

2. Install dependencies
```python
pip install -r requirements_superres.txt
```

3. Run the python file
```console
python reconstruction_superres.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --resolution{} \
 --download_model {True}{False} \
 --clean_model {True}{False} \
 --model_prefix_s3 pretrained-models/fsrcnn_x4.pb
 --local_model_path model.pb
```
ex/
```console
python reconstruction_superres.py \
--output_prefix_s3 reconstructed-videos/benchmark/fsrcnn/car/ \
--resolution 1920 1080 \
--model_prefix_s3 pretrained-models/fsrcnn_x4.pb \
--local_model_path model.pb
--clean_model True
```

- model_prefix_s3 available for this module:
  - pretrained-models/edsr_x4.pb
  - pretrained-models/espcn_x4.pb
  - pretrained-models/fsrcnn_x4.pb
  - pretrained-models/lapsrn_x4.pb


### Running FastSRGAN

- **Reccomended EC2 image-id ami-0f598ecd07418eba2**

1. Move to working directory
```console
cd reconstruction/fastsrgan
```

2. Install dependencies
```python
pip install -r requirements_fastsrgan.txt
```

3. Run the python file

```console
python fastsrgan.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --download_model {True}{False} \
 --clean_model {True}{False} \
 --model_prefix_s3 pretrained-models/fastsrgan.h5
 --local_model_path fastsrgan.h5
```
ex/
```console
python fastsrgan.py \
--output_prefix_s3 reconstructed-videos/benchmark/fastsrgan/car/ \
--model_prefix_s3 pretrained-models/fastsrgan.h5 \
--local_model_path fastsrgan.h5
--clean_model True
```

### Yolo Model

Please read the Yolo model readme for more instructions.

### Mediapipe Model

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

4. cleanup  local files

```
clean_files(path_to_orginal_folder,path_to_modified_folder)
```

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

# **Leto**
----------------------------------
# Project Structure

```
├──  leto				contains all modules that facilites all functionality to achieve leto's goal
│   ├── benchmarking
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
│       ├── video_quality_functions.py
│
│   ├── reduction
│       ├── ffmpeg_resolution_downsampler
│           ├── requirements_ffmpeg_resolution_downsampler.txt
│           ├── ffmpeg_resolution_downsampler.py
│       ├── fps_bitrate
│           ├── fps_bitrate.py
│           ├── app-fps_bitrate.py
│           ├── requirements.txt
│           ├── README.md
│       ├── cv2_jpg_reduction
│           ├── cv2_jpg_reduction.py
│           ├── requirements_cv2_jpg_reduction.txt
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
|
│
├──  tests				contains unit tests
│   ├── test_get_meta_data.py
│   ├── conftest.py
│   ├── test_data
│      ├── test_video.mp4

```
----------------------------------

# Reduction to Reconstruction Mapping:

ffmpeg resolution downsampler(240p,360p,420p,720p,1080p)(lanczos,bicubic) --> fastsrgan, superres(edsr_x4,espcn_x4,fsrcnn_x4,lapsrn_x4), opencv_resoltion_upscaler, realbasicvser(very slow).

fps_bitrate --> Parings with frame interpolation coming soon!


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
python ffmpeg_resolution_downsampler.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --quality{} \
 --algorithm{}
```
ex/
```console
python ffmpeg_resolution_downsampler.py \
--input_prefix original-videos/benchmark/car/ \
--output_prefix_s3 reduced-videos/ffmpeg-resolution-downsampler-480p-lanczos/benchmark/car \
--quality 480p \
--algorithm lanczos
```

Default input: s3://leto-dish/original-videos/benchmark/car/

Default output: s3://leto-dish/reduced-videos/benchmark/ffmpeg-360/car/

### Running fps_bitrate reduction

1. Move to working directory:
```console
cd leto/reduction/fps_bitrate
```

2. Install requirements:

```console
pip install -r requirements_fps_bitrate.txt
```

4. Execute the runner method, ***app_fps_bitrate.py***

```console
python app_fps_bitrate.py
```

### Running cv2_jpg_compression reduction

1. Move to working directory:
```console
cd leto/reduction/cv2_jpg_reduction/
```

3. Install requirements:

```console
pip install -r requirements_cv2_jpg_reduction.txt
```

4. Execute the runner method, ***cv2_jpg_reduction.py***

```console
python cv2_jpg_reduction.py
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
python fps_bitrate.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --fps{} \
 --bitrate{}
```
ex/
```console
python fps_bitrate.py \
--input_prefix original-videos/benchmark/car/ \
--output_prefix_s3 reduced-videos/fps_bitrate-30-0/benchmark/car \
--fps 30 \
--bitrate 0
```

Default input: s3://leto-dish/original-videos/benchmark/car/

Default output: s3://leto-dish/reduced-videos/benchmark/fps_bitrate-30-0/car/

----------------------------------
# Reconstruction Modules

- Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4

- Default cloud output: s3://leto-dish/reconstructed-videos/benchmark/misc/car/resized_480x360_video_benchmark_car.mp4


### Running opencv resolution upscaler

- **Reccomended EC2 image-id ami-0f598ecd07418eba2**

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

- **Reccomended EC2 image-id ami-0f598ecd07418eba2**

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
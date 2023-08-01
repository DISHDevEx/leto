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

- Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4

- Default cloud outout: s3://leto-dish/reconstructed-videos/benchmark/misc/car/resized_480x360_video_benchmark_car.mp4

### Running RealBasicVSR

- **Very High Quality SR, takes a very LONG time**

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

# **Leto**
----------------------------------

## Mapping Between Compatible Reduction and Reconstruction Methods


| Reduction Method         | Applicable Reconstruction Method(s)    |
|--------------|-----------|
| [ffmpeg_resolution_downsampler](./reduction/ffmpeg_resolution_downsampler/) (360p,420p,640p,720p) | [opencv_resolution_upscaler](./reconstruction/opencv_resolution_upscaler/) <br> [superres](./reconstruction/superres/) (4 different configurations) <br> [fastsrgan](./reconstruction/fastsrgan/) <br> [realbasicvsr](./reconstruction/realbasicvsr/) (small sample size, takes a long time)     |
| [fps_bitrate](./reduction/fps_bitrate/)      | Linear Frame interpolation <br> NN based frame interpolation   |
| NN Codec                   |  NN Codec |
| [cv2_jpg_reduction](./reduction/cv2_jpg_reduction/)                   |  N/A  |
|Background Subtraction  |  Background Addition  |



## Running Reduction and Reconstruction Methods Using ***config.ini***:

For existing Reduction and Reconstruction Methods, use the following guide to modify the [***config.ini***](config.ini) file prior to method execution.  If you have a new method you would like to get working with the ***config.ini***, then follow the instructions outlined in the [next section](#using-configini-with-new-reduction-and-reconstruction-methods) to do so.

For existing methods, perform the following prior to method execution:

1. Open the [***config.ini***](config.ini) and identify the appropriate section for the method you would like to execute.
    - sections are denoted by the following pattern ```[<METHOD_CLASS>.<METHOD_NAME>]```; so, if you want to use a ***reduction*** method called ***fps_bitrate***, the ***config.ini*** file section should be titled something like ```[reduction.fps_bitrate]```.

2. Modify the values for the keys you would like to change.  For example, if you would like to execute ***fps_bitrate*** with an ***fps*** value of 15 and a ***bitrate*** value of 0 (for 10x reduction), then the ***config.ini*** file should be modified to resemble:

```ini
[reduction.fps_bitrate]
; method specific parameters:
fps = 15
bitrate = 0

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
      An example for a ***reduction*** method named ***fps_bitrate***:
      ```
      [reduction.fps_bitrate]
      ```  
  - Under your new section, define the arguments/variables you will need in your method.  This takes the form of a key/value format.  An example section is given below.  Comments are denoted using ```;``` and inline comments are allowed using ```;``` as well.  Sub-sections can be denoted with comments for readability, but this has no effect on accessing the configurations.
  - Interpolation of values is supported with ***configparser***, here is the [documentation for the syntax of interpolation](https://docs.python.org/3/library/configparser.html#interpolation-of-values).

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
--input_prefix_s3 original-videos/benchmark/car/ \
--output_prefix_s3 reduced-videos/fps_bitrate-30-0/benchmark/car \
--fps 30 \
--bitrate 0
```

Default input: s3://leto-dish/original-videos/benchmark/car/

Default output: s3://leto-dish/reduced-videos/benchmark/fps_bitrate-30-0/car/
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
python cv2_jpg_reduction.py \
 --input_bucket_s3{} \
 --input_prefix_s3{} \
 --output_bucket_s3{} \
 --output_prefix_s3{} \
 --quality{}
 --crf{}
```
ex/

```console
python cv2_jpg_reduction.py \
--input_prefix_s3 original-videos/benchmark/car/ \
--output_prefix_s3 reduced-videos/fps_bitrate-30-0/benchmark/car \
--quality 15 \
--crf 28 \

----------------------------------
# Reconstruction Modules

- Default cloud input: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/resized_480x360_video_benchmark_car.mp4

- Default cloud output: s3://leto-dish/reconstructed-videos/benchmark/misc/car/resized_480x360_video_benchmark_car.mp4


### Running opencv resolution upscaler

- **Reccomended EC2 image-id ami-0f598ecd07418eba2**
- **Please use ec2-user!**

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
- **Please use ec2-user!**

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
- **Please use ec2-user!**

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
- **Please use ec2-user!**

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

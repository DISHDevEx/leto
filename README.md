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

2. Run reconstruction_setup.sh to setup environment
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


### Yolo Model

Please read the Yolo model readme for more instructions.

### Mediapipe Model

Please read the Mediapipe model readme for more instructions.


## Running utils file
Run the following command to import Evaluator class and Get PSNR and SSIM
```
from utils import Evaluator
video_eval = Evaluator()
original_file = 'path/to/input/file'
reconstructed_file = 'path/to/output/file' ( Add your orginal and recontructed file)
### for calculating PSNR and SSIM for videos in S3 bucket
 
original_file_path, reconstructed_file_path = video_eval.read_files_from_s3_match(bucket_name, prefix_to_original_file, prefix_reduced_file)

psnr = video_eval.calculate_psnr(original_file_path, reconstructed_file_path)
print(f"Video PSNR: {psnr} dB")
ssim = video_eval.calculate_video_ssim(original_file_path, reconstructed_file_path)
print(f"SSIM: {ssim}")
## cleanup 
video_eval.clean_files(path_to_orginal_folder,path_to_modified_folder)
````

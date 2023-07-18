# **Leto**
----------------------------------
# Project Structure

```
├──  leto				contains video class and processor class that manage from loading, processing and uploading
│   ├── downstream_model
│       ├── mediapipe
│           ├── object_detection.py
│           ├── visualize.py
│           ├── Dockerfile_mp
│           ├── requirements_mp.txt
│
│   ├── reduction
│       ├── method_1
│           ├── source_code.py
│           ├── requirement_method_1.txt
│           ├── Dockerfile_method_1
│   ├── reconstruction
│
├──  runner_notebooks
│   ├── leto-demo.ipynb
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

Default input: s3://leto-dish/original-videos/benchmark/

Default output: s3://leto-dish/reduced-videos/benchmark/ffmpeg-resolution-downsampler/


----------------------------------
# Reconstruction Modules

- RealBasicVSR

### Running RealBasicVSR 

1. Move to working directory
```console
cd leto/reconstruction/RealBasicVSR
```

2. Run reconstruction_setup.sh to setup environment
```console
bash reconstruction_setup.sh
```

3. Run preprocessing function
```console
python realbasicvsr_preprocessing.py
```
- Default cloud input: s3://leto-dish/reduced-videos/benchmark/downsampler

- Note Pre Processing will save local video and a 200mb pretrained model

4. Run inference module on desired vido
```console
python reconstruction_realbasicvsr.py {input_dir} {output_dir}
```
Example:
```console
python reconstruction_realbasicvsr.py  ./reduced_videos/resized_480x360_Video_Benchmark_Car.mp4 ./reconstructed_videos/recon_resized_480x360_Video_Benchmark_Car.mp4
```

-  Necessary arguments: input_dir, output_dir

5. Run postprocessing function
```console
python realbasicvsr_postprocessing.py
```
- Default cloud output: s3://leto-dish/reconstructed-videos/benchmark/downsampler

- Optional argument to delete locally saved pretrained model (from preprocessing).
- Note Postprocessor will delete any locally saved video**

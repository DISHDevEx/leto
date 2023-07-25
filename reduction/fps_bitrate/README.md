# Reduction using fps_bitrate

## Introduction

This module takes a list of videos from a set S3 bucket, processes them by reducing FPS and Bitrate of the original videos and then saving to a seperate set S3 bucket.  In future versions, dynamic allocation of S3 buckets can be added.  

As a user, you will need access to READ/WRITE to S3 in the E1-Dev DISH AWS environment.  Use this context in the below [Run Book](#run-book) when asked to provide AWS Credentials.  In the event you are using this module in an AWS native environment, for instance Cloud9 or Sagemaker, you may not need to provide AWS credentials for correct authentication and access to S3.

## Run Book

1. If needed, provide AWS credentials

2. Ensure you are in the ***fps_bitrate*** directory:

2. Install requierments:

```console
pip install -r requirements.txt
```

3. execute the runner method, ***app_fps_bitrate.py***

```console
python app_fps_bitrate.py
```

Processed videos will now be saved to the set output S3 path.  Dynamic allocation of S3 paths can be added in future versions.
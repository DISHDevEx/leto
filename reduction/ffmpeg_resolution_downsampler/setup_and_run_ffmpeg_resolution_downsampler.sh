#!/bin/bash

#This script should be executed in Amazon Linux (amzn2-ami-kernel-5.10-hvm-2.0.20230628.0-x86_64-gp2) operating system with python3>=3.9.*

#This script will install the pre-requisites required to execute the 'leto - reduction module - ffmpeg_resolution_downsampler.py' script and then execute the python script,
#which will take the input video file from the source S3 path, reduce the resolution, label it, and then upload the downsampled video to the destination S3 path.

#Install pip
sudo yum -y update
if which pip &> /dev/null || sudo yum install -y python3-pip; then
    echo "Successfully installed pip";pip --version
else
    echo " Failed to install pip"
fi
#Install mesa-libGL
if sudo yum -y install mesa-libGL; then
    echo "Successfully installed mesa-libGL"
else
    echo " Failed to install mesa-libGL"
fi
#Download requirements and python script files into the working directory
if curl -o requirements_ffmpeg_resolution_downsampler.txt https://raw.githubusercontent.com/DISHDevEx/leto/main/reduction/ffmpeg_resolution_downsampler/requirements_ffmpeg_resolution_downsampler.txt; then
    echo "Successfully downloaded requirements_ffmpeg_resolution_downsampler.txt file"
else
    echo "Failed to download requirements_ffmpeg_resolution_downsampler.txt file"
fi
#
if curl -o ffmpeg_resolution_downsampler.py https://raw.githubusercontent.com/DISHDevEx/leto/main/reduction/ffmpeg_resolution_downsampler/ffmpeg_resolution_downsampler.py; then
    echo "Successfully downloaded ffmpeg_resolution_downsampler.py file"
else
    echo "Failed to download ffmpeg_resolution_downsampler.py file"
fi
#Installing requirements
if python3 -m pip install -r requirements_ffmpeg_resolution_downsampler.txt; then
    echo "Successfully installed requirements"
else
    echo "requirements installation failed"
fi
#Make sure all installed libraries are in path
if export PATH=/home/ssm-user/.local/bin:$PATH; then
    echo "Libraries are in path."
else
    echo "Libraries failed to move to path."
fi
#Run ffmpeg_resolution_downsampler.py script
if python3 ffmpeg_resolution_downsampler.py; then
    echo "Downsampling of the source video files is completed and respective downsampled video files are uploaded to the destination path."
    echo "Video file source path: https://s3.console.aws.amazon.com/s3/buckets/leto-dish?region=us-east-1&prefix=original-videos/benchmark/car/&showversions=false"
    echo "Video file destination path: https://s3.console.aws.amazon.com/s3/buckets/leto-dish?region=us-east-1&prefix=reduced-videos/benchmark/ffmpeg-resolution-downsampler/car/&showversions=false"
fi
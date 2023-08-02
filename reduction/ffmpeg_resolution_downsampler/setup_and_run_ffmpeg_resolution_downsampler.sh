#Shell script to deploy the Leto Reduction - ffmpeg_resolution_downsampler module in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash

#This script should be executed in Amazon Linux (amzn2-ami-kernel-5.10-hvm-2.0.20230628.0-x86_64-gp2) operating system with python3>=3.7.*

#This script will install the pre-requisites required to execute the 'leto - reduction module - ffmpeg_resolution_downsampler.py' script and then execute the python script,
#which will take the input video file from the source S3 path, reduce the resolution, label it, and then upload the downsampled video to the destination S3 path.

#Install pip
sudo yum update -y
if which pip &> /dev/null || sudo yum install -y python3-pip; then
    echo "Successfully installed pip";pip --version
else
    echo " Failed to install pip"
fi
#Install mesa-libGL
if sudo yum install -y mesa-libGL; then
    echo "Successfully installed mesa-libGL"
else
    echo " Failed to install mesa-libGL"
fi
#Download requirements and python script files into the working directory
if curl -o /home/ssm-user/requirements_ffmpeg_resolution_downsampler.txt https://raw.githubusercontent.com/DISHDevEx/leto/main/reduction/ffmpeg_resolution_downsampler/requirements_ffmpeg_resolution_downsampler.txt; then
    echo "Successfully downloaded requirements_ffmpeg_resolution_downsampler.txt file"
else
    echo "Failed to download requirements_ffmpeg_resolution_downsampler.txt file"
fi
#
if curl -o /home/ssm-user/ffmpeg_resolution_downsampler.py https://raw.githubusercontent.com/DISHDevEx/leto/main/reduction/ffmpeg_resolution_downsampler/ffmpeg_resolution_downsampler.py; then
    echo "Successfully downloaded ffmpeg_resolution_downsampler.py file"
else
    echo "Failed to download ffmpeg_resolution_downsampler.py file"
fi
#Install requirements
if python3 -m pip install -r /home/ssm-user/requirements_ffmpeg_resolution_downsampler.txt; then
    echo "Successfully installed requirements"
else
    echo "Requirements installation failed"
fi
#Add libraries path to the environment variable PATH temporarily
if export PATH=/home/ssm-user/.local/bin:$PATH; then
    echo "Libraries are temporarily added to the PATH temporarily."
else
    echo "Failed to add the Libraries to the PATH temporarily."
fi
#Run ffmpeg_resolution_downsampler.py script
cd /home/ssm-user
if python3 /home/ssm-user/ffmpeg_resolution_downsampler.py; then
    echo "Downsampling of the source video files is completed and respective downsampled video files are uploaded to the destination path."
else
    echo "ffmpeg_resolution_downsampler.py script execution failed."
fi
#Add libraries path to the environment variable 'PATH' permanently
if echo "export PATH=/home/ssm-user/.local/bin:$PATH;" >> ~/.bashrc; then
    echo "Libraries path is permanently added to the environment variable PATH to support recurring execution of downsampler script."
    source ~/.bashrc
else
    echo "Failed to permanently add Libraries path to the environment variable PATH to support recurring execution of downsampler script."
fi
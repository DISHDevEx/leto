#Shell script to deploy the Leto Reconstruction - opencv_resolution_upscaler module in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash

#This script should be executed in Amazon Linux (amzn2-ami-kernel-5.10-hvm-2.0.20230628.0-x86_64-gp2) operating system with python3>=3.7.*

#This script will install the pre-requisites required to execute the 'leto - reconstruction module - opencv_resolution_upscaler.py' script and then execute the python script,
#which will take the input video file from the source S3 path, upscale the resolution, and then upload the reconstructed video to the destination S3 path.
#
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
if curl -o /home/ssm-user/requirements_opencv_resolution_upscaler.txt https://raw.githubusercontent.com/DISHDevEx/leto/main/reconstruction/opencv_resolution_upscaler/requirements_opencv_resolution_upscaler.txt; then
    echo "Successfully downloaded requirements_opencv_resolution_upscaler.txt file"
else
    echo "Failed to download requirements_opencv_resolution_upscaler.txt file"
fi
#
if curl -o /home/ssm-user/opencv_resolution_upscaler.py https://raw.githubusercontent.com/DISHDevEx/leto/main/reconstruction/opencv_resolution_upscaler/opencv_resolution_upscaler.py; then
    echo "Successfully downloaded opencv_resolution_upscaler.py file"
else
    echo "Failed to download opencv_resolution_upscaler.py file"
fi
#Install requirements
if python3 -m pip install -r /home/ssm-user/requirements_opencv_resolution_upscaler.txt; then
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
#Run opencv_resolution_upscaler.py script
cd /home/ssm-user
if python3 /home/ssm-user/opencv_resolution_upscaler.py; then
    echo "Recounstruction of the source video files is completed and respective reconstructed video files are uploaded to the destination path."
else
    echo "opencv_resolution_upscaler.py script execution failed."
fi
#Add libraries path to the environment variable 'PATH' permanently
if echo "export PATH=/home/ssm-user/.local/bin:$PATH;" >> ~/.bashrc; then
    echo "Libraries path is permanently added to the environment variable PATH to support recurring execution of opencv_resolution_upscaler script."
    source ~/.bashrc
else
    echo "Failed to permanently add Libraries path to the environment variable PATH to support recurring execution of opencv_resolution_upscalar script."
fi

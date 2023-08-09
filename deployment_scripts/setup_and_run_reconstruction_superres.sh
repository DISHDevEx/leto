#Shell script to deploy the Leto Reconstruction - reconstruction_superres module in the target AWS EC2 instance.
#Version: v1.0.0
#
#!/bin/bash

#This script should be executed in Amazon Linux (amzn2-ami-kernel-5.10-hvm-2.0.20230628.0-x86_64-gp2) operating system with python3>=3.7.*

#This script will install the pre-requisites required to execute the 'leto - reconstruction module - reconstruction_superres.py' script and then execute the python script,
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
#Install git
if sudo yum install -y git; then
    echo "Successfully installed git"
else
    echo " Failed to install git"
fi
#Download requirements and python script files into the working directory
cd /home/ssm-user
git clone https://github.com/DISHDevEx/leto.git
cd leto
git checkout ankita/update_superres
git pull
rm -rf .github
rm -rf benchmarking
rm -rf reconstruction/opencv_resolution_upscaler
rm -rf reconstruction/realbasicvsr
rm -rf reduction
rm -rf tests
rm -rf .gitignore
rm -rf .pylintrc
rm -rf CODE_OF_CONDUCT.md
rm -rf HISTORY.md
rm -rf LICENSE
rm -rf README.md
rm -rf __init__.py
cd reconstruction/superres/
echo "Successfully downloaded the python scripts"
#Install requirements
if python3 -m pip install -r requirements_superres.txt; then
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
#Run reconstruction_superres.py script
if python3 reconstruction_superres.py; then
    echo "Reconstruction of the source video files is completed and respective reconstructed video files are uploaded to the destination path."
else
    echo "reconstruction_superres.py script execution failed."
fi
#Add libraries path to the environment variable 'PATH' permanently
if echo "export PATH=/home/ssm-user/.local/bin:$PATH;" >> ~/.bashrc; then
    echo "Libraries path is permanently added to the environment variable PATH to support recurring execution of reconstruction_superres script."
    source ~/.bashrc
else
    echo "Failed to permanently add Libraries path to the environment variable PATH to support recurring execution of reconstruction_superres script."
fi
#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Set variable values
source ~/.bashrc
WORKING_DIRECTORY="/home/ec2-user/leto"
FILE_PATH=$1
cd $WORKING_DIRECTORY
#Run the python script
conda activate leto
conda env list
python3 $WORKING_DIRECTORY/$1
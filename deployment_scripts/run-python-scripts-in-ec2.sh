#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Activate & deactivate base before activating leto, so that system will recognize the 'conda activate' command
source activate base
conda deactivate
#Activate leto environment
conda activate leto
#Set variable values and run the python script
WORKING_DIRECTORY="/home/ec2-user/leto"
FILE_PATH=$1
cd $WORKING_DIRECTORY
python3 $WORKING_DIRECTORY/$1
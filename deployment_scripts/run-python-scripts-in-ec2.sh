#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Set PATH, variable values and run the python script
export PATH="/home/ec2-user/.local/bin:$PATH"
WORKING_DIRECTORY="/home/ec2-user/leto"
FILE_PATH=$1
cd $WORKING_DIRECTORY
python3 $WORKING_DIRECTORY/$1
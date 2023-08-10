#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Set variable values and run the python script
WORKING_DIRECTORY="/home/ec2-user/leto"
FILE_PATH=$1
cd $WORKING_DIRECTORY
sudo python3 $WORKING_DIRECTORY/$1
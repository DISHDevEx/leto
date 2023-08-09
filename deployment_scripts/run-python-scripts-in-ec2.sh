#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Run the python script
WORKING_DIRECTORY="/home/ec2-user/leto"
cd $WORKING_DIRECTORY
python3 /home/ec2-user/leto/reduction/ffmpeg_resolution_downsampler/ffmpeg_resolution_downsampler.py
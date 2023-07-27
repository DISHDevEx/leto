Reduction module - ffmpeg_resolution_downsampler.py deployment in AWS EC2 instance with shell scripts:
------------------------------------------------------------------------------------------------------
The reduction module - https://github.com/DISHDevEx/leto/tree/main/reduction/ffmpeg_resolution_downsampler - is used to take the input video file from the source S3 path, reduce the resolution,
label it, and then upload the processed video to the destination S3 path.

The module is deployed using shell scripts in AWS EC2 instance as per the below steps,

1.Create an AWS EC2 Amazon Linux instance manually in AWS account with the following configuration,

a)Instance Type: t3.small

b)AMI: amzn2-ami-kernel-5.10-hvm-2.0.20230628.0-x86_64-gp2

2.Save the ‘setup_and_run_ffmpeg_resolution_downsampler.sh’ file in the user home directory. You can find the user home directory by executing this command: echo $HOME

3.Provide execution permissions to the shell script using this command: chmod +x setup_and_run_ffmpeg_resolution_downsampler.sh, and then execute it.

4.Post script execution, validate the changes by checking if the processed video files are uploaded to the respective destination S3 path.
  You can cross-check the file list in that target path by comparing the file names in the source S3 path.

 Recurring execution of ffmpeg_resolution_downsampler.py script in the same AWS EC2 instance:
---------------------------------------------------------------------------------------------
After the initial setup and execution, for recurring execution of 'ffmpeg_resolution_downsampler.py' script in the same AWS EC2 instance,
please execute following commands in the user home directory.

a)source ~/.bashrc

b)python3 ffmpeg_resolution_downsampler.py
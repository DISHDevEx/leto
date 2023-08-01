Reconstruction module - reconstruction_superres.py deployment in AWS EC2 instance with shell scripts:
--------------------------------------------------------------------------------------------------------
The reduction module - https://github.com/DISHDevEx/leto/tree/main/reconstruction/superres - is used to take the reduced video file as input from the source S3 path, upscale the resolution, and then upload the processed video to the destination S3 path.

The module is deployed using shell scripts in AWS EC2 instance as per the below steps,

1.Create an AWS EC2 Amazon Linux instance manually in AWS account with the following configuration,

a)Instance Type: t3.small

b)AMI: amzn2-ami-kernel-5.10-hvm-2.0.20230628.0-x86_64-gp2

2.Save the ‘setup_and_run_reconstruction_superres.sh’ file in the user home directory - '/home/ssm-user'.

3.You can execute the script directly with this command: bash setup_and_run_reconstruction_superres.sh

4.Post script execution, validate the changes by checking if the processed video files are uploaded to the respective destination S3 path.
  You can cross-check the file list in that target path by comparing the file names in the source S3 path.

 Recurring execution of reconstruction_superres.py script in the same AWS EC2 instance:
------------------------------------------------------------------------------------------
After the initial setup and execution, for recurring execution of 'reconstruction_superres.sh' script in the same AWS EC2 instance,
please execute following commands in the user home directory - '/home/ssm-user'.

a)source ~/.bashrc

b)python3 reconstruction_superres.py
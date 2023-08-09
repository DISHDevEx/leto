Reduction modules deployment in AWS EC2 instance with shell scripts:
--------------------------------------------------------------------
The [reduction](https://github.com/DISHDevEx/leto/tree/main/reduction/) modules are used to take the input video file from the source S3 path, reduce the resolution, label it, and then upload the processed video to the destination S3 path.

The module is deployed using shell scripts in AWS EC2 instance as per the below steps,

1.Create an AWS EC2 Amazon Linux instance using 'Create new EC2 instance' workflow in the leto repository with the following parameters:

a)Enter name of the EC2: "Enter desired name for EC2 instance"

b)Enter AMI id for the EC2: {e.g. ami-0f34c5ae932e6f0e4}

c)Enter EC2 instance type: {e.g. t3.small}

2.Login to the EC2 using the Session Manager to ensure it is up and running as expected. 
  Also, copy the respective EC2 instance id as we have to pass it as a parameter in the next step.

3.Then execute the 'deploy-reduction-modules-in-ec2' workflow in the leto repository with following parameters:

a)Enter EC2 instance id: "Enter respective EC2 instance id" #Instance id entry is required

b)Enter Git branch name: "Enter desired branch name" #This entry is optional and default branch value is 'main'

c)Enter reduction module name: "Enter respective reduction module name" #Reduction module name entry is required

  Note: This reduction module 'name' should be the same as the respective module 'folder name' under the 'reduction' directory in the GitHub - leto repository.

4.The 'deploy-reduction-modules-in-ec2.sh' script will do the following steps in the EC2:

a)Download the 'deploy-reduction-modules-in-ec2.sh' to EC2

b)Execute the 'deploy-reduction-modules-in-ec2.sh' script in EC2

5.Post workflow execution, validate the changes by loging to the respective EC2 instance and check if the respective module requirements are installed in the EC2 or not.

GitHub workflow to run the Leto - Python scripts in the target AWS EC2 instance:
--------------------------------------------------------------------------------
To run the python scripts which are already deployed in the target AWS EC2 instance, execute the 'run-python-scripts-in-ec2.yml' workflow in the leto repository with following parameters:

a)Enter EC2 instance id: "Enter respective EC2 instance id" #Instance id entry is required

b)Enter python file path in leto repository: "Enter the file path" #Python file path entry is mandatory and the file path should be based on it's location in the leto repository

  #Example: The file path of 'cv2_jpg_reduction.py' in 'leto' repository is, 'reduction/cv2_jpg_reduction/cv2_jpg_reduction.py'
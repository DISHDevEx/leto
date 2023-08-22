Prerequisite:
-------------
In order to run the ssm commands in GitHub workflow as 'ec2-user', you need to configure your AWS Session Manager to run as 'ec2-user' by following below steps:

a)Open AWS Systems Manager > Go to Session Manager page > Got to Preferences tab > Click Edit and select checkbox for 'Enable Run As support for Linux instances'

b)Now, enter 'ec2-user' as value for 'Operating system user name'

c)Scroll down and update 'ssm-user' as 'ec2-user' in the 'Linux shell profile' section > Scroll down and click 'Save' button.

Reduction/Reconstruction modules deployment in AWS EC2 instance with shell scripts:
-----------------------------------------------------------------------------------
The [reduction](https://github.com/DISHDevEx/leto/tree/main/reduction/) modules are used to take the input video file from the source S3 path, reduce the resolution, label it, and then upload the processed video to the destination S3 path.

The [reconstruction](https://github.com/DISHDevEx/leto/tree/main/reconstruction/) modules are used to take the input video file from the source - reduced videos S3 path, upscale the resolution, label it, and then upload the reconstructed video to the destination S3 path.

The reduction/reconstruction modules are deployed using shell scripts in AWS EC2 instance as per the below steps:

1.Create an AWS EC2 Amazon Linux instance using 'Create new EC2 instance' workflow in the leto repository with the following parameters:

a)Enter name of the EC2: "Enter desired name for EC2 instance"

b)Enter AMI id for the EC2: {e.g. ami-0f34c5ae932e6f0e4} 

  Note: 'ami-0f598ecd07418eba2' is the recommended AMI id for reduction/reconstruction modules that don't have any dependency on 'PyTorch' library for deployment and execution

        'ami-051619310404cab17' is the recommended AMI id for reduction/reconstruction modules that have dependency on 'PyTorch' library for deployment and execution

c)Enter EC2 instance type: {e.g. t3.small}

2.Login to the EC2 instance as 'ec2-user' to ensure it is up and running as expected. 
  Also, copy the respective EC2 instance id as we have to pass it as a parameter in the next step.

3.Then execute the 'deploy-leto-modules-in-ec2' workflow in the leto repository with following parameters:

a)Enter EC2 instance id: "Enter respective EC2 instance id" #Instance id entry is required

b)Enter Git branch name: "Enter desired branch name" #This entry is optional and default branch value is 'main'

c)Select module type: Select either 'Reduction' or 'Reconstruction' from drowpdown in the UI as applicable #Module type selection is required

d)Enter module name: "Enter respective module name" #Module name entry is required

  Note: This reduction module 'name' should be the same as the respective module 'folder name' under the 'reduction'/'reconstruction' directory in the GitHub - leto repository.

e)Select library required: Select either 'None' or 'Tensorflow' or 'PyTorch' from drowpdown in the UI as applicable #Module type selection is required #Library selection is required

  Note: Option 'None' refers to the modules that don't have any dependency on 'Tensorflow' or 'PyTorch' libraries for deployment and execution. Select respective library name for the modules that have dependency on 'Tensorflow' or 'PyTorch' libraries for deployment and execution.

4.The 'deploy-leto-modules-in-ec2.sh' script will do the following steps in the EC2:

a)Download the 'deploy-leto-modules-in-ec2.sh' to EC2

b)Execute the 'deploy-leto-modules-in-ec2.sh' script in EC2

5.Post workflow execution, validate the changes by loging to the respective EC2 instance and check if the respective module requirements are installed in the EC2 or not.

GitHub workflow to run the Leto - Python scripts in the target AWS EC2 instance:
--------------------------------------------------------------------------------
To run the python scripts which are already deployed in the target AWS EC2 instance, execute the 'run-python-scripts-in-ec2.yml' workflow in the leto repository with following parameters:

a)Enter EC2 instance id: "Enter respective EC2 instance id" #Instance id entry is required

b)Select library required: Select either 'None' or 'Tensorflow' or 'PyTorch' from drowpdown in the UI as applicable #Module type selection is required #Library selection is required

  Note: Option 'None' refers to the modules that don't have any dependency on 'Tensorflow' or 'PyTorch' libraries for deployment and execution. Select respective library name for the modules that have dependency on 'Tensorflow' or 'PyTorch' libraries for deployment and execution.

c)Enter python file path in leto repository: "Enter the file path" #Python file path entry is mandatory and the file path should be based on it's location in the leto repository

  #Example: The file path of 'cv2_jpg_reduction.py' in 'leto' repository is, 'reduction/cv2_jpg_reduction/cv2_jpg_reduction.py'
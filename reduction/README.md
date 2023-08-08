Reduction modules deployment in AWS EC2 instance with shell scripts:
--------------------------------------------------------------------
The reduction modules - https://github.com/DISHDevEx/leto/tree/main/reduction/ - are used to take the input video file from the source S3 path, reduce the resolution,
label it, and then upload the processed video to the destination S3 path.

The module is deployed using shell scripts in AWS EC2 instance as per the below steps,

1.Create an AWS EC2 Amazon Linux instance using 'Create new EC2 instance' workflow in the leto repository with the following configuration,

a)Enter name of the EC2: <Enter desired name for EC2 instance>

b)Enter AMI id for the EC2: ami-0f34c5ae932e6f0e4

c)Enter EC2 instance type: t3.small

2.Login to the EC2 using the Session Manager to ensure it is up and running as expected.

3.Update the EC2 instance id value in the leto repository - github secret 'REDUCTION_INSTANCE_ID'

4.Then execute the 'deploy-reduction-modules-in-ec2' workflow in the leto repository by selecting the respective reduction module name

5.The workflow will do the following steps in the EC2,

a)Download the 'deploy-reduction-modules-in-ec2.sh' to EC2

b)Execute the 'deploy-reduction-modules-in-ec2.sh' script in EC2

6.The 'deploy-reduction-modules-in-ec2.sh' script will do the following steps in the EC2,

7.Post workflow execution, validate the changes by loging to the respective EC2 instance and check if the respective module requirements are installed or not.
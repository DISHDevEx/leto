
#Shell script to deploy the Leto - Reduction modules in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Install the prerequisite packages
sudo yum update -y
sudo yum install -y mesa-libGL
sudo yum install -y git
git --version
sudo yum install -y python3-pip
python3 --version
pip3 --version
#Set 'WORKING_DIRECTORY' and 'MODULE_NAME' variables 
WORKING_DIRECTORY="/home/ssm-user/leto"
MODULE_NAME=$1
#If the leto directory exists, then do git pull else do git clone
if [-d "$WORKING_DIRECTORY"]; then
    echo "Doing 'git pull' as the leto directory already exists." 
    cd $WORKING_DIRECTORY
    git pull
    echo "Git pull is completed successfully."
else
    echo "Cloning leto repository into this path $WORKING_DIRECTORY"
    cd $WORKING_DIRECTORY
    git clone https://github.com/DISHDevEx/leto.git
    echo "Git clone is completed successfully."
fi
#Deploy the requirements for selected module
echo "Installing requirements for $MODULE_NAME module."
cd $WORKING_DIRECTORY/reduction/$MODULE_NAME
python3 -m pip install -r requirements*.txt
echo "Successfully installed requirements for $MODULE_NAME module."


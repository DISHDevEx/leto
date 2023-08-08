
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
WORKING_DIRECTORY="/home/ssm-user"
GIT_BRANCH=$1
MODULE_NAME=$2
#If the leto directory exists, then do git pull else do git clone
if [ -d "$WORKING_DIRECTORY/leto" ]; then
    echo "Doing 'git pull' as the leto directory already exists." 
    cd $WORKING_DIRECTORY/leto
    git pull
    echo "Git pull is completed successfully."
else
    echo "Cloning leto repository into this path $WORKING_DIRECTORY"
    cd $WORKING_DIRECTORY
    git clone https://github.com/DISHDevEx/leto.git
    echo "Git clone is completed successfully."
fi
#Switch git branch if 'GIT_BRANCH' is not null
if [ "$GIT_BRANCH" != "main" ]; then
    cd $WORKING_DIRECTORY/leto
    pwd
    echo "Switching branch to $GIT_BRANCH"
    git switch $GIT_BRANCH
    echo "Branch switched to $GIT_BRANCH"
    cd ..
    pwd
else
    cd $WORKING_DIRECTORY/leto
    GIT_BRANCH="main"
    echo "Switching branch to $GIT_BRANCH"
    git switch $GIT_BRANCH
    echo "Branch switched to $GIT_BRANCH"
    cd ..
    pwd
fi
#Deploy the requirements for selected module
echo "Installing requirements for $MODULE_NAME module."
#Install requirements
#Find the requirements file of the module
cd $WORKING_DIRECTORY/leto/reduction/$MODULE_NAME && fVar=$(find -type f -name 'requirements*.txt');
FILE_NAME=${fVar:2}
if python3 -m pip install -r $WORKING_DIRECTORY/leto/reduction/$MODULE_NAME/$FILE_NAME; then
    echo "Successfully installed requirements for $MODULE_NAME module."
else
    echo "Requirements installation failed for $MODULE_NAME module."
fi
#Add libraries path to the environment variable PATH temporarily
if [ "$(tail -1 ~/.bashrc)" != "unset rc" ]; then
    echo "Libraries path is already added permanently to the environment variable PATH to support recurring execution of python script."
    source ~/.bashrc
else
if export PATH=/home/ssm-user/.local/bin:$PATH; then
    echo "Libraries are temporarily added to the PATH temporarily."
else
    echo "Failed to add the Libraries to the PATH temporarily."
fi
#Add libraries path to the environment variable 'PATH' permanently
if echo "export PATH=/home/ssm-user/.local/bin:$PATH;" >> ~/.bashrc; then
    echo "Libraries path is permanently added to the environment variable PATH to support recurring execution of python script."
    source ~/.bashrc
else
    echo "Failed to permanently add Libraries path to the environment variable PATH to support recurring execution of python script."
fi
fi


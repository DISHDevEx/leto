#Shell script to deploy the Leto - Reconstruction modules in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Install the prerequisite packages
sudo yum update -y
sudo yum install -y mesa-libGL
sudo yum install -y git
git --version
#Insall Miniconda3 to create a virtual conda environment
cd /home/ec2-user
curl -sL "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh" > "Miniconda3.sh"
bash Miniconda3.sh -b -p $HOME/miniconda3
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
conda update conda -y
rm -rf Miniconda3.sh
#Create new virtual conda environment
conda create --name leto python=3.10.12 -y
#Activate & deactivate base before activating leto, so that system will recognize the 'conda activate' command
source activate base
conda deactivate
#Activate leto environment
conda activate leto
#Set variable values 
WORKING_DIRECTORY="/home/ec2-user"
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
#Switch git branch if 'GIT_BRANCH' is not equal to 'main'
if [ "$GIT_BRANCH" != "main" ]; then
    cd $WORKING_DIRECTORY/leto
    echo "Switching branch to $GIT_BRANCH"
    git switch $GIT_BRANCH
    echo "Branch switched to $GIT_BRANCH"
    cd ..
else
    cd $WORKING_DIRECTORY/leto
    GIT_BRANCH="main"
    echo "Switching branch to $GIT_BRANCH"
    git switch $GIT_BRANCH
    echo "Branch switched to $GIT_BRANCH"
    cd ..
fi
#Deploy the requirements for module in EC2
echo "Installing requirements for $MODULE_NAME module."
#Install requirements
#Find the requirements file of the module
cd $WORKING_DIRECTORY/leto/reconstruction/$MODULE_NAME && fVar=$(find -type f -name 'requirements*.txt');
FILE_NAME=${fVar:2}
if python3 -m pip install -r $WORKING_DIRECTORY/leto/reconstruction/$MODULE_NAME/$FILE_NAME; then
    echo "Successfully installed requirements for $MODULE_NAME module."
else
    echo "Requirements installation failed for $MODULE_NAME module."
fi


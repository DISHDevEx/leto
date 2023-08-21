#Shell script to deploy the Leto - Reduction/Reconstruction modules in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Set variable values 
WORKING_DIRECTORY="/home/ec2-user"
GIT_BRANCH=$1
MODULE_TYPE=$(echo $2 | tr '[:upper:]' '[:lower:]') #Converting value from uppercase to lowercase
MODULE_NAME=$3
LIBRARY_REQUIRED=$4
TENSORFLOW_REQUIRED=false
PYTORCH_REQUIRED=false
#Update variable values based on input parameter value
if [ "$LIBRARY_REQUIRED" == "Tensorflow" ]; then
    TENSORFLOW_REQUIRED=true
elif [ "$LIBRARY_REQUIRED" == "PyTorch" ]; then
    PYTORCH_REQUIRED=true
fi
#Functions used for Reduction/Reconstruction modules deployment in AWS EC2 instance
install_common_packages(){
    #Update yum 
    sudo yum update -y
    #Install git
    if git --version &>/dev/null; then
        git --version
        echo "git package is already installed"
    else
        sudo yum install -y git
        git --version
        echo "Successfully installed git"
    fi
    #Install mesa-libGL
    MESA_CHECK=$(sudo yum list installed mesa-libGL.x86_64 | grep mesa-libGL.x86_64 | wc -l)
    if [ "$MESA_CHECK" -gt 0 ];then
        echo "mesa-libGL package is already installed"
    else
        sudo yum install -y mesa-libGL
        sudo yum list installed mesa-libGL.x86_64 | grep mesa-libGL.x86_64
        echo "Successfully installed mesa-libGL"
    fi
    #Install pip
    if pip --version &>/dev/null; then
        pip --version
        echo "pip package is already installed"
    elif pip3 --version &>/dev/null; then     
        pip3 --version
        echo "pip package is already installed"
    else
        sudo yum install -y python3-pip
        pip3 --version
        echo "Successfully installed pip"
    fi
}
setup_virtual_env(){
    #Insall Miniconda3 to create a virtual conda environment
    #Check if the miniconda3 is already installed
    cd /home/ec2-user
    if [ -d "/home/ec2-user/miniconda3/envs/leto" ]; then
        source ~/.bashrc
        echo "conda environment named 'leto' already exist"
        echo "Activating 'leto' environment"
        conda activate /home/ec2-user/miniconda3/envs/leto
        conda env list
    else
        echo "Installing Miniconda3"
        curl -sL "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh" > "Miniconda3.sh"
        bash Miniconda3.sh -b -p $HOME/miniconda3
        echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
        source ~/.bashrc
        conda update conda -y
        source ~/.bashrc
        conda init
        source ~/.bashrc
        echo "conda deactivate" >> ~/.bashrc
        rm -rf Miniconda3.sh
        #Create new virtual conda environment
        conda create --name leto python=3.10.12 -y
        conda env list
        #Activate leto environment
        conda activate /home/ec2-user/miniconda3/envs/leto
        conda env list
    fi
}
deploy_leto_repository(){
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
}
install_module_requirements(){
    #Deploy the requirements for module in EC2
    echo "Installing requirements for $MODULE_NAME module."
    #Install requirements
    #Find the requirements file of the module
    cd $WORKING_DIRECTORY/leto/$MODULE_TYPE/$MODULE_NAME && fVar=$(find -type f -name 'requirements*.txt');
    FILE_NAME=${fVar:2}
    if $1 -m $2 install -r $WORKING_DIRECTORY/leto/$MODULE_TYPE/$MODULE_NAME/$FILE_NAME; then
        $2 list
        echo "Successfully installed requirements for $MODULE_NAME module."
    else
        echo "Requirements installation failed for $MODULE_NAME module."
    fi
}
deploy_tensorflow_dependent_module(){
echo "Activating tensorflow"
source activate tensorflow
python -c "import tensorflow as tf; print(tf.__version__)"
install_common_packages
deploy_leto_repository
install_module_requirements python pip
}
deploy_pytorch_dependent_module(){
echo "Activating pytorch"
source activate pytorch
python -c "import torch; print(torch.__version__)"
install_common_packages
deploy_leto_repository
install_module_requirements python3 pip3
}
#Check for module dependency and proceed further accordingly
if [ "$TENSORFLOW_REQUIRED" == "true" ] || [ "$PYTORCH_REQUIRED" == "true" ]; then
    if [ "$TENSORFLOW_REQUIRED" == "true" ]; then
        deploy_tensorflow_dependent_module
    elif [ "$PYTORCH_REQUIRED" == "true" ]; then
        deploy_pytorch_dependent_module
    fi
else
    install_common_packages
    setup_virtual_env
    deploy_leto_repository
    install_module_requirements python pip
fi
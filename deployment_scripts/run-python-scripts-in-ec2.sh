#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v1.0.0
#
#!/bin/bash
#Set variable values
source ~/.bashrc
LIBRARY_REQUIRED=$1
FILE_PATH=$2
WORKING_DIRECTORY="/home/ec2-user/leto"
#Check for module dependency and proceed further accordingly
if [ "$LIBRARY_REQUIRED" == "Tensorflow" ]; then
    cd $WORKING_DIRECTORY
    echo "Activating tensorflow"
    source /opt/tensorflow/bin/activate
    python -c "import tensorflow as tf; print(tf.__version__)"
    #Run the python script
    python $WORKING_DIRECTORY/$FILE_PATH
elif [ "$LIBRARY_REQUIRED" == "PyTorch" ]; then
    cd $WORKING_DIRECTORY
    echo "Activating pytorch"
    conda activate /opt/conda/envs/pytorch
    python -c "import torch; print(torch.__version__)"
    #Run the python script
    python $WORKING_DIRECTORY/$FILE_PATH
elif [ "$LIBRARY_REQUIRED" == "None"]; then
    cd $WORKING_DIRECTORY
    conda activate /home/ec2-user/miniconda3/envs/leto
    conda env list
    #Run the python script
    python $WORKING_DIRECTORY/$FILE_PATH
fi
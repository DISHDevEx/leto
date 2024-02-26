#Shell script to run the Leto - Python scripts in the target AWS EC2 instance
#Version: v2.0.0
#
#!/bin/bash
#Set variable values
source ~/.bashrc
LIBRARY_REQUIRED=$1
FILE_PATH=$2
WORKING_DIRECTORY="/home/ec2-user/leto"
#Check for module dependency and proceed further accordingly
case $LIBRARY_REQUIRED in
  "Tensorflow")
    cd $WORKING_DIRECTORY
    echo "Activating tensorflow"
    source /opt/tensorflow/bin/activate
    python3 -c "import tensorflow as tf; print(tf.__version__)"
    #Run the python script
    python3 $WORKING_DIRECTORY/$FILE_PATH
    ;;
  "PyTorch")
    cd $WORKING_DIRECTORY
    echo "Activating pytorch"
    conda activate /opt/conda/envs/pytorch
    python3 -c "import torch; print(torch.__version__)"
    #Run the python script
    python3 $WORKING_DIRECTORY/$FILE_PATH
    ;;
  "None")
    cd $WORKING_DIRECTORY
    conda activate /home/ec2-user/miniconda3/envs/leto
    conda env list
    #Run the python script
    python3 $WORKING_DIRECTORY/$FILE_PATH
    ;;
  *) # Default case if none of the above matches
    echo "Please pass correct input parameter for 'library_required'"
    ;;
esac
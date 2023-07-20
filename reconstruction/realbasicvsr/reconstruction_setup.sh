#!/bin/sh
activate base
conda install pytorch==1.7.1 torchvision==0.8.2 torchaudio==0.7.2 cudatoolkit=10.1 -c pytorch
pip install openmim
mim install mmcv-full
pip install mmedit
apt-get update && apt-get install libgl1
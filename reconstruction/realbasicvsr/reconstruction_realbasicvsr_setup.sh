#!/bin/sh
pip install --upgrade pip
pip install torch torchvision torchaudio 
pip install openmim
mim install mmcv-full
pip install mmedit
pip install aEye
apt-get update && apt-get install libgl1
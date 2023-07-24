#!/bin/sh
activate base
pip install torch torchvision torchaudio 
pip install openmim
mim install mmcv-full
pip install mmedit
pip install aEye
apt-get update && apt-get install libgl1
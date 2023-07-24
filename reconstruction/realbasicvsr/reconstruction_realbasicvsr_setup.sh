#!/bin/sh
<<<<<<< HEAD
pip install --upgrade pip
=======
activate base
>>>>>>> 9c9abaa (corrected deletion of .pth file)
pip install torch torchvision torchaudio 
pip install openmim
mim install mmcv-full
pip install mmedit
pip install aEye
apt-get update && apt-get install libgl1
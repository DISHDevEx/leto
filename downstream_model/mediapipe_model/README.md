# Yolo

'You Only Look Once' a powerful computer vision model.

### **Demo**

1. Install the necessary requirements

```console
!pip install -r requirements_yolo.txt
```

2. Import all utlity

```console
import boto3
import cv2
from aEye import Video
from aEye import Aux
from .object_detection import object_detection
```

3. Import video from s3

```console
aux = Aux()
video_list_s3 = aux.load_s3(bucket = 'aeye-data-bucket', prefix = 'input_video/')
```

4. Load in mediapipe model

Download the pretrained mediapipe model
https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/latest/efficientdet_lite0.tflite

store this file path into a variable.

5. Apply the model on the loaded video

```console
object_detection( model_path, video_list_s3[0].get_file(), video_list_s3[0].title)
#this will apply, draw the bounding box and write a single video the loaded.
```

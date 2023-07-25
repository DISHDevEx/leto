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
from .yolo import Yolo
from .yolo import pipeline
```

3. Import video from s3

```console
aux = Aux()
video_list_s3 = aux.load_s3(bucket = 'aeye-data-bucket', prefix = 'input_video/')
```

4. Load in yolo model

```console
model = Yolo()
model.load_model_weight('yolov8s.pt')  #this model .pt is a pretrained model from yolov8 to detect 80 objects
```

5. Apply the model on the loaded video

```console
pipeline( video_list_s3[0].get_file(), model, video_list_s3[0].title)
#this will apply, draw the bounding box and write a single video the loaded.
```

# Yolo

'You Only Look Once' a powerful computer vision model.

### **Demo**

1. Clone the repo

```console
!git clone git@github.com:DISHDevEx/leto.git
!cd leto
```

2. Install the necessary requirements

```console
!pip install -r downstream_model/yolo/requirements_yolo.txt
```

3. Import all utlity

```console
import boto3
import cv2
from aEye import Video
from aEye import Aux
from downstream_model.yolo import Yolo
from downstream_model.yolo import pipeline
```

4. Import video from s3

```console
aux = Aux()
video_list_s3 = aux.load_s3(bucket = 'aeye-data-bucket', prefix = 'input_video/')
```

5. Load in yolo model

```console
model = Yolo()
model.load_model_weight('yolov8s.pt')  #this model .pt is a pretrained model from yolov8 to detect 80 objects
```

6. Apply the model on the loaded video

```console
result  = pipeline( video_list_s3[0].get_file().strip("'"), model, video_list_s3[0].title)
#This will apply, draw the bounding box, and return the result in a dictionary.
#This will also make and save a new video with the name of video_list_s3[0].title if extra parameter of save_video = True is passed in.

```

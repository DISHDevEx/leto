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
!pip install -r downstream_model/mediapipe_model/requirements_yolo.txt
```

3. Import all utlity

```console
import boto3
import cv2
from aEye import Video
from aEye import Aux
from .object_detection import object_detection
```

4. Import video from s3

```console
aux = Aux()
video_list_s3 = aux.load_s3(bucket = 'aeye-data-bucket', prefix = 'input_video/')
```

5. Load in mediapipe model

Download the pretrained mediapipe model
https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/latest/efficientdet_lite0.tflite

store this file path into a variable.

6. Apply the model on the loaded video

```console
object_detection( model_path, video_list_s3[0].get_file().strip("'"), video_list_s3[0].title)
#This will apply, draw the bounding box, and return the result in a dictionary.
#This will apply, draw the bounding box, and return the result in a dictionary.#This will also make and save a new video with the name of video_list_s3[0].title if extra parameter of save_video = True is passed in.
```

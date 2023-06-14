# aEye

Extensible Video Processing Framework with Additional Features Continuously Deployed

### **Project Structure**

```
├──  aEye				contains vidoe class and processor class that manage from loading, processing and uploading
│   ├── processor.py
│   ├── video.py
├──  tests				contains unit tests
│   ├── test.py
<<<<<<< HEAD
├──  data				contains a temp location for video to save before deleting and uploading to S3
=======
>>>>>>> 8e4c128 (adds readme)
```

### **inital project setup**

1. clone/pull this repo to local machine

```console
git clone https://github.com/DISHDevEx/aEye.git
```

2. Install the necessary requirements

```console
<<<<<<< HEAD
!pip install -r requirements.txt
```

3. Run below to import in jyputer-notebook
=======
!pip install -r requirement.txt
```

3. Run below in jyputer-notebook to import
>>>>>>> 8e4c128 (adds readme)

```console
import boto3
import cv2
from aEye.video import Video
from aEye.processor import Processor
```

4. Initalize the processor class

```console
<<<<<<< HEAD
process = Processor()
=======
P = processor()
>>>>>>> 8e4c128 (adds readme)
```

5. Load the video from the desired bucket and folder and resize them to desired ratio

```console
<<<<<<< HEAD
process.load_and_resize(bucket = 'aeye-data-bucket', prefix = 'input_video/', x_ratio = .6, y_ratio = .5)
=======
P.load(bucket = 'aeye-data-bucket', prefix = 'input_video/', x_ratio = .6, y_ratio = .5)
>>>>>>> 8e4c128 (adds readme)
```

6. Upload the result to the desire bucket

```console
<<<<<<< HEAD
process.upload(bucket = 'aeye-data-bucket')
=======
P.upload(bucket = 'aeye-data-bucket')
>>>>>>> 8e4c128 (adds readme)
```

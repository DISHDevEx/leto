# aEye

Extensible Video Processing Framework with Additional Features Continuously Deployed

### **Project Structure**

```
├──  leto				contains video class and processor class that manage from loading, processing and uploading
│   ├── mediapipe
│      ├── object_detection.py
│      ├── visualize.py
├──  runner_notebooks
│   ├── leto-demo.ipynb
├──  tests				contains unit tests
│   ├── test_get_meta_data.py
│   ├── conftest.py
│   ├── test_data
│      ├── test_video.mp4
├── lambda_function.py
├── setup.py
```

### **Inital project setup**


### **Docker Image Setup**

The docker image is built automatically via github workflow action on every tag push.
The rough sequence is below:

    1) The workflow action will build a wheel file based on setup.py,
    2) Then it will create a docker image based on the dockerfile.
    3) Finally it will push the image to ECR (currently, this will be loaded in ECR: Leto).

Please refer to mp-to-ecr.yml to get the exact sequences of the github workflow action, the dockerfile for the exact content in the docker image and setup.py for the exact built version.

### **Lambda Function**

Please refer to lambda_function.py for the logic of the lambda function.

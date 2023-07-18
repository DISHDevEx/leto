# leto

### **Project Structure**

```
├──  leto				contains video class and processor class that manage from loading, processing and uploading
│   ├── downstream_model
│       ├── mediapipe
│           ├── object_detection.py
│           ├── visualize.py
│           ├── Dockerfile_mp
│           ├── requirements_mp.txt
│
│   ├── reduction
│       ├── fps_bitrate
│           ├── fps_bitrate.py
│           ├── app_fps_bitrate.py
│           ├── requirements.txt
│           ├── README.md
│   ├── reconstruction
│
├──  runner_notebooks
│   ├── leto-demo.ipynb
│
├──  tests				contains unit tests
│   ├── test_get_meta_data.py
│   ├── conftest.py
│   ├── test_data
│      ├── test_video.mp4

```


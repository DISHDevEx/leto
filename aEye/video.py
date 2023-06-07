import cv2
import numpy as np

class Video:
<<<<<<< HEAD
    """
    @:constructor file
        file is the path name for the file
    """

    def __init__(self,file):
        """

        """
        self.file = file
        self.meta_data = 'insert by James'
        self.cap = cv2.VideoCapture(file)
        if self.cap is None:
            print("Error opening video stream or file")


    def resize(self, x_ratio, y_ratio):
        """
        this method will resize the current video by multiplying 
        the current x and y by the input x_ratio 

        input: FLOAT
        non negative and non zero value

        """
        width = int(self.cap.shape[1] * x_ratio / 100)
        height = int(self.cap.shape[0] * y_ratio / 100)
        dim = (width, height)
        self.cap = cv2.resize(self.cap , dim, interpolation = cv2.INTER_AREA)

    def extract_time_frame(self):
        """
        this method will extract frames with time
        """

    def extract_index_frame(self):
        """
        this method will extract frames with index
        """
=======
    def __init__(self,file,name:str, codec: str, width: int, height: int, duration: float, frames: int) -> None:
        self.file = file
        self.meta_data = 'insert by James'
        self.name = name
        self.codec = codec
        self.width = int(width)
        self.height = int(height)
        self.duration = float(duration)
        self.frames = int(frames)
        self.fps = self.frames / self.duration

    def getSize(self):
        print("Video Resolution:", self.width, 'x', self.height)

    def getVideoDetails(self):
        print("Metadata for video: " + self.name)
        self.getSize()
        print("Encoding Format:", self.codec, "Duration (s):", self.duration, "with a total of", self.frames,
              "frames! (" + str(self.fps) + " FPS)")

>>>>>>> 2ef4d7d6113d393ecb046274b35ace2dba5d1025

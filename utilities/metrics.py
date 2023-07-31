# Current directory is brought to root level to avoid import issues
import subprocess
import sys
# get git repo root level
root_path = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, check=False).stdout.rstrip('\n')
#add git repo path to use all libraries
sys.path.append(root_path)
from downstream_model.yolo import pipeline
from downstream_model.mediapipe_model import object_detection

def calculateMAC_yolo(video,model):
    """
    Calculates average confidence of a video by calculating average confidence of each frame
    
    Parameters
    ----------
    video : string
    The input video
    model : model with weights
    The yolo model with appropriate weights
    Returns
    ---------
    mean_average_confidence: float
    The calculated  mean average confidence(MAC) of the video 
    """
    mean_average_confidence = 0
    # Get object detection parameters from pipeline method    
    result = pipeline(video.get_file().strip("'"), model, video.title)
    # Obtain average precions of all frames in a list
    frame_average_confidence = [result[res] for res in result] 
    # Average confidence of the video is the sum of average confidence of each frame/ total frames
    if len(frame_average_confidence):
        mean_average_confidence = sum(frame_average_confidence)/len(frame_average_confidence)
    return mean_average_confidence


def calculateMAC_mp(video,model):
    """
    Calculates average confidence of a video by calculating average confidence of each frame
    
    Parameters
    ----------
    video : string
    The input video
    model : model with weights
    The mediapipe model with appropriate weights
    Returns
    ---------
    mean_average_confidence: float
    The calculated  mean average confidence(MAC) of the video 
    """
    mean_average_confidence = 0
    # Get object detection parameters from object_detection method    
    result = object_detection(video.get_file().strip("'"), model, video.title)
    # Obtain average precions of all frames in a list
    frame_average_confidence = [result[res] for res in result] 
    # Average confidence of the video is the sum of average confidence of each frame/ total frames
    if len(frame_average_confidence):
        mean_average_confidence = sum(frame_average_confidence)/len(frame_average_confidence)
    return mean_average_confidence
   
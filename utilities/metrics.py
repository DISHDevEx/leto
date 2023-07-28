# Current directory is brought to root level to avoid import issues
import subprocess
import sys
# get git repo root level
root_path = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, check=False).stdout.rstrip('\n')
#add git repo path to use all libraries
sys.path.append(root_path)
from downstream_model import pipeline

def calculateAP(video,model):
    """
    Calculates average precision of a video by calculating average precision of each frame
    
    Parameters
    ----------
    video : string
    The input video
    model : model with weights
    The desired downstream model with appropriate weights
    Returns
    ---------
    video_average_confidence: float
    The calculated average precision of the video 
    """
    video_average_confidence = 0
    # Get object detection parameters from pipeline method    
    result = pipeline(video.get_file().strip("'"), model, video.title)
    # Obtain average precions of all frames in a list
    frame_average_confidence = [result[res][-1] for res in result] 
    # Average confidence of the video is the sum of average confidence of each frame/ total frames
    if len(frame_average_confidence):
        video_average_confidence = sum(frame_average_confidence)/len(frame_average_confidence)
    return video_average_confidence
   
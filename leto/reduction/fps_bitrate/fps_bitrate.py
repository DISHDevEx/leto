from aEye import Labeler 
import logging

def fps_bitrate(video_list, fps=30, bitrate=0):

    labeler = Labeler()

    try:
        if fps <= 0:
            raise Exception
        labeler.change_fps(video_list, fps)
    except Exception:
        logging.exception("")

    try:
        if bitrate < 0:
            raise Exception
            
        labeler.set_bitrate(video_list, bitrate)
    except Exception:
        logging.exception("")
    
    return video_list
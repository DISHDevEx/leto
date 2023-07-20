from aEye import Labeler 
import logging

def fps_bitrate(video_list, fps=30, bitrate=0):

    """
    Wrapper method for the change_fps and set_bitrate methods in aEye.Labeler.

    This method addes labels to the input videos for fps and bitrate rectuion.
    The lables are then exectured in the runner method to process the videos.
    Default settings of fps=30 and bitrate=0 result in the output videos having
    30 frames per second and a 10x reduction in bitrate.

    Parameters
    ----------
        video_list: list
            list of input videos
        
        fps: int | default --> 30
            desired Frames per Second (fps) for output videos to be clocked to
        
        bitrate: int | default --> 0
            desired bitrate for the videos. This is given in Kb, so setting it to 1.5 Mb for exmaple should be
            1500, not 1.5. 
            
            Default Setting: Setting to 0 will do a 10x bitrate reduction
        


    Returns
    ----------
        video_list: list
            list of videos with changes labeled for bitrate and framerate reduction; to be processed in runner method
    """

    labeler = Labeler()

    try:
        if fps <= 0:
            raise Exception
        labeler.change_fps(video_list, fps)
    except Exception:
        logging.exception("unable to process with given fps; must be > 0")

    try:
        if bitrate < 0:
            raise Exception
            
        labeler.set_bitrate(video_list, bitrate)
    except Exception:
        logging.exception("unable to process with given bitrate; must be >= 0")
    
    return video_list
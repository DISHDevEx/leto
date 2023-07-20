from aEye import Labeler 
import logging

def fps_bitrate(video_list, fps=30, bitrate=0):

    """
    This method will predict the model based on the parameter and the given data.
    
    The data can be inputted with many format; it can be a video, an image and even a list of images.
    It can also take in an entire directory path.
    
    Please refer to https://docs.ultralytics.com/modes/predict/#inference-sources 
    for the full list of valid sources, videos, and images format.

    Please also refer to prediction_parameter_input.py for the entire list of all possible **parameter can take in
    and how to use this method properly!


    Natively, if a video and 'save=True' is passed in as a parameter, then yolo will save the video as avi.
    Therefore, the pipeline.py will only pass in each frame in this method, so we can customize and save the result for our own use cases.

    Parameters
    ----------
        data: str
            The path of the desired data.

        **parameter: dict of argument
            An unpacked  dict of argument that are native from ultralics framework


    Returns
    ----------
        result: list
            A list of Detection objects
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
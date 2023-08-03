"""
Module contains the pipeline to faciliate and apply a yolo model to predict frame by frame by using cv2.
This pipeline will call visualize_yolo to visualize the result from the prediction.
"""

from .visualize import visualize_yolo
import cv2


def pipeline(input_video, model, output_video, save_video=False):
    """
    This functions opens the video frame by frame and applies yolo model to each frame.

    Parameters
    ----------
        input_video: string
            The path for the video file or its presigned url if video is in s3.

        model: YOLO
            The desired yolo model with its weight.

        output_video: string
            The path name

        save_video: boolean
            The condition to save video.
    Returns
    ---------
        output_data: list
        The average confidence of each frame    
    """

    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
    frame_index = 0
    output_data = {}

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            # change the channel in the format that yolo accepts
            im2 = frame[..., ::-1]

            # Perform object detection on the video frame.
            detection_result = model.predict_(im2, verbose=False, device=None)

            copy_image = frame.copy()
            annotated_image, average_confidence = visualize_yolo(copy_image, detection_result)
            if save_video:
                out.write(annotated_image)

            output_data[frame_index] = average_confidence
            frame_index += 1
        # Break the loop
        else:
            break
    # When everything done, release
    # the video capture object
    cap.release()
    out.release()
    return output_data

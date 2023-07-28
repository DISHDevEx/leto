"""
Module contains the pipeline to faciliate and apply a yolo model to predict frame by frame by using cv2.
This pipeline will call visualize_yolo to visualize the result from the prediction.
"""

from .visualize import visualize_yolo
import cv2

def pipeline(input_video,  model, output_video, save_video = False ):

    '''  
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
        output_data: dict
            The diction of the prediction in the format below.
            {
                0 : [ bounding_box_1, bounding_box_2, etc  ], 
                1 : [ bounding_box_1, bounding_box_2, etc  ],

            }

            The key value of integer understands the frame index of the video.
            Each frame index contains a list of bounding box predicted. 
            Each frame index could contains any amount of predicted box, therefore its value is in a List format.
            
            Each bounding box is a List that contains all the neccessariy elements to make a bounding box.
            The format is below:
                bounding_box_1 = [ start_point_x, start_point_y, end_point_x, end_point_y, probability, category_name ]
    '''

    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
    frame_index = 0
    output_data = {}

    while (cap.isOpened()):

        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            # change the channel in the format that yolo accepts
            im2 = frame[..., ::-1]

            # Perform object detection on the video frame.
            detection_result = model.predict_(im2, verbose = False, device = None)

            copy_image = frame.copy()
            annotated_image, bounding_box_data,average_confidence = visualize_yolo(copy_image, detection_result)
            if save_video:
                out.write(annotated_image)

            output_data[frame_index] = bounding_box_data,average_confidence
            frame_index += 1
        # Break the loop
        else:
            break
    # When everything done, release
    # the video capture object
    cap.release()
    out.release()
    return output_data
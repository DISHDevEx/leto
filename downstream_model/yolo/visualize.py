"""
Module contains the visualizer to annotate the frame with the yolo prediction.
"""

import cv2
import numpy as np

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red


def visualize_yolo(image, detection_result) -> np.ndarray:
    """Draws bounding boxes on the input image and return it.
    Parameters
    ----------
        Image: cv2 image
            The input RGB image.
        detection_result: List
            The list of all bounding boxes entities to be visualize from yolo.

    Returns
    ---------
        image: cv2 image
            The orginal cv2 Image with bounding boxes draw in along with the corresponding probability and name.

<<<<<<< HEAD
        
        average confidence: float
            The average confidence of all the labels detected by the model  
=======

        bounding_box_data: List
            This is a list of all the bounding box in a single frame.
            This could have any amount of bounding box.
            The format is below.
            bounding_box_data = [  b1, b2, etc      ]

            Each b_ value represent a list of all the neccessariy elements to make a bounding box.
            Its format is below.
            b1 = [ start_point_x, start_point_y, end_point_x, end_point_y, probability, category_name ]



>>>>>>> main
    """

    shape = detection_result[0].orig_shape
    bounding_box_data = []
    sum_confidence = 0
    average_confidence = 0
    for i, _ in enumerate(detection_result[0].boxes.cls):
        # Draw bounding_box
        x, y, w, h = detection_result[0].boxes.xyxyn[i]

        start_point = int(x.item() * shape[1]), int(y.item() * shape[0])
        end_point = int(w.item() * shape[1]), int(h.item() * shape[0])

        cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

<<<<<<< HEAD
        # Calculate confidence per label and sum the confidence scores of all labels
        probability = round(detection_result[0].boxes.conf[i].item(), 2)
        sum_confidence += probability  
    # Calculate the average confidence of all labels in the frame 
    if len(detection_result[0]):
        average_confidence = sum_confidence/len(detection_result[0])
    return image,average_confidence
=======
        # Draw label and score
        category_name = detection_result[0].names[
            detection_result[0].boxes.cls[i].item()
        ]
        probability = round(detection_result[0].boxes.conf[i].item(), 2)
        result_text = category_name + " (" + str(probability) + ")"
        text_location = (MARGIN + start_point[0], MARGIN + ROW_SIZE + start_point[1])
        cv2.putText(
            image,
            result_text,
            text_location,
            cv2.FONT_HERSHEY_PLAIN,
            FONT_SIZE,
            TEXT_COLOR,
            FONT_THICKNESS,
        )
        bounding_box_data.append(
            [
                start_point[0],
                start_point[1],
                end_point[0],
                end_point[1],
                probability,
                category_name,
            ]
        )

    return image, bounding_box_data
>>>>>>> main

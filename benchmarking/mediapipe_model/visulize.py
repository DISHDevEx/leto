"""
Draw bounding boxes.
"""

import cv2
import numpy as np

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red


def visualize(image, detection_result):
    """Draws bounding boxes on the input image and return it.
    Args:
      image: The input RGB image.
      detection_result: The list of all "Detection" entities to be visualize.

    Returns:
      image: a cv2 image
        Image with bounding boxes.

      average_confidence : float
            The average confidence of all the labels detected by the model

    """
    sum_confidence =0
    
    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        #print('score', category.score)
        #print('probability',probability)
        sum_confidence += probability
    #print(sum_confidence)
        # Calculate the average confidence of all labels in the frame
    if len(detection_result.detections):
        average_confidence = sum_confidence / len(detection_result.detections)
        average_confidence = round(average_confidence,2)
    return image, average_confidence

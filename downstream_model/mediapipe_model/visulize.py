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

    bounding_box_data: List
      This is a list of all the bounding box in a single frame.
      This could have any amount of bounding box.
      The format is below.
      bounding_box_data = [  b1, b2, etc      ]
      
      Each b_ value represent a list of all the neccessariy elements to make a bounding box.
      Its format is below.
      b1 = [ start_point_x, start_point_y, end_point_x, end_point_y, probability, category_name ]

    
  """
  bounding_box_data = []
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
    result_text = category_name + ' (' + str(probability) + ')'
    text_location = (MARGIN + bbox.origin_x,
                     MARGIN + ROW_SIZE + bbox.origin_y)
    cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)
    bounding_box_data.append([start_point[0],start_point[1],end_point[0] , end_point[1], probability, category_name ])

  return image, bounding_box_data






from object_detection import object_detection


mAC = object_detection("/Users/hamza.khokhar/Downloads/efficientdet_lite0.tflite","/Users/hamza.khokhar/Downloads/violence00.mp4", "")

frame_average_confidence = [mAC[res] for res in mAC]
# Average confidence of the video is the sum of average confidence of each frame/ total frames
if len(frame_average_confidence):
    mean_average_confidence = sum(frame_average_confidence) / len(
        frame_average_confidence
    )
print(mean_average_confidence)

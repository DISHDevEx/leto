import cv2

def background_addition(video_path, image_path, output_path):
    """This methods adds static background to masked image
    Parameters
    Videopath: path to image 
    Imagepath: static background

    Returns:
    Reconstructed videos with background added
    
    """
    cap = cv2.VideoCapture(video_path)
    image = cv2.imread(image_path)

# Get the dimensions of the video frames
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create a VideoWriter object to save the output
    output_path = output_path
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize the image to match the video frame size
        resized_image = cv2.resize(image, (frame_width, frame_height))
        
        # Combine the image and video frames
        combined_frame = cv2.addWeighted(frame, 1, resized_image, 0.5, 0)
        
        out.write(combined_frame)

        cv2.imshow('Combined Video', combined_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()





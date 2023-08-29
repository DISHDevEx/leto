import cv2

def linear_interpolation(frame_a, frame_b, alpha):
    return cv2.addWeighted(frame_a, 1 - alpha, frame_b, alpha, 0)


# Load video
    video_path = 'input_video.mp4'
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    # Create VideoWriter to save interpolated video
    output_path = 'interpolated_video.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 video
    out = cv2.VideoWriter(output_path, fourcc, frame_rate, frame_size)

    # Read frames and perform interpolation
    ret, frame_a = cap.read()
    while ret:
        ret, frame_b = cap.read()
        
        if not ret:
            break
        
        # Perform linear interpolation
        num_interpolated_frames = 3  # Number of interpolated frames between each pair of frames
        for i in range(num_interpolated_frames + 1):
            alpha = i / (num_interpolated_frames + 1)
            interpolated_frame = linear_interpolation(frame_a, frame_b, alpha)
            out.write(interpolated_frame)
        
        frame_a = frame_b

    # Release VideoCapture and VideoWriter
    cap.release()
    out.release()

    print("Interpolation complete. Interpolated video saved as:", output_path)

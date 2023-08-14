import subprocess

input_video_path = 'resized_480x360_Video_Benchmark_Car.mp4'  # Update with your input video path
output_frames_folder = 'frames'  # Update with your output frames folder

# Create the output frames folder if it doesn't exist
subprocess.run(['mkdir', '-p', output_frames_folder])

# Run the FFmpeg command to convert the video to frames
command = [
    'ffmpeg',
    '-i', input_video_path,
    f'{output_frames_folder}/frame%04d.png'
]
subprocess.run(command)

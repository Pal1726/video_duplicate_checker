# frame_analysis.py

import cv2
import numpy as np

def compare_frames(video1_path, video2_path):
    # Open videos using OpenCV
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)
    
    # Initialize frame-by-frame comparison variables
    frame_diff_sum = 0
    total_frames = 0

    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break  # End of videos

        # Resize frames to a common resolution for comparison
        frame1 = cv2.resize(frame1, (640, 480))
        frame2 = cv2.resize(frame2, (640, 480))

        # Convert frames to grayscale for better comparison
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between frames
        frame_diff = cv2.absdiff(gray1, gray2)
        non_zero_diff = np.count_nonzero(frame_diff)

        # Sum the number of differing pixels
        frame_diff_sum += non_zero_diff
        total_frames += 1

    cap1.release()
    cap2.release()

    # Calculate frame comparison score as percentage of matching pixels
    if total_frames == 0:
        return {"status": "error", "message": "No frames to compare."}

    avg_diff = frame_diff_sum / total_frames
    frame_similarity = (1 - avg_diff / (640 * 480)) * 100  # Similarity percentage

    return {"status": "success", "frame_similarity": frame_similarity}

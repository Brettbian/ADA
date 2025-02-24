import functions_framework
import gdown
import os
from flask import request, jsonify
import cv2
import base64
import numpy as np

def download_video_from_drive(drive_url, output_path):
    """Downloads a video from Google Drive given its shareable link."""
    gdown.download(drive_url, output_path, quiet=False)

@functions_framework.http
def process_video(request):
    """HTTP Cloud Function to download a video from Google Drive and return frames."""
    request_json = request.get_json()
    if not request_json or 'video_url' not in request_json:
        return "Missing 'video_url' in request payload", 400

    video_url = request_json['video_url']
    output_path = "/tmp/downloaded_video.mp4"
    
    try:
        download_video_from_drive(video_url, output_path)
        imgs = take_screenshot(output_path)
        
        # Convert frames to base64-encoded strings for JSON serialization
        # one_frame = frame_to_base64(imgs[0])
        frame_data = [frame_to_base64(frame) for frame in imgs]
        return jsonify({"frames": frame_data}), 200
        # return one_frame, 200
        
    except Exception as e:
        return f"Failed to download video: {str(e)}", 500

def take_screenshot(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    # Extract key frames at k-second intervals
    frame_interval = int(fps * 2)  # Capture every 20 seconds
    frames = []
    timestamps = []

    for i in range(0, frame_count, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            continue
        timestamp = i / fps
        frames.append(frame)
        timestamps.append(timestamp)

    cap.release()
    return frames

def frame_to_base64(frame):
    """Convert a frame to a base64-encoded string."""
    _, buffer = cv2.imencode('.jpg', frame)
    base64_string = base64.b64encode(buffer).decode('utf-8')
    return base64_string
import os
import tempfile
import numpy as np
from typing import List, Dict, Any, Tuple
from app.utils.logger import logger

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None


async def extract_frames_from_video_bytes(video_bytes: bytes, max_frames: int = 64, target_size: Tuple[int, int] = (224, 224)) -> List[np.ndarray]:
    """
    Extract sequence of RGB frame arrays from video bytes payload (MP4, WEBM).
    """
    if not video_bytes:
        raise ValueError("Video payload is empty.")

    if not OPENCV_AVAILABLE:
        logger.warning("OpenCV is not installed. Frame extraction returning mock sequence.")
        mock_frame = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
        return [mock_frame] * min(max_frames, 10)

    frames: List[np.ndarray] = []
    # Write video bytes to temporary file for OpenCV VideoCapture
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(video_bytes)
        tmp_path = tmp_file.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video stream from temp file {tmp_path}")
            raise ValueError("Corrupted or unsupported video stream.")

        count = 0
        while cap.isOpened() and count < max_frames:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if target_size:
                rgb_frame = cv2.resize(rgb_frame, target_size, interpolation=cv2.INTER_AREA)

            frames.append(rgb_frame)
            count += 1

        cap.release()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    logger.info(f"Successfully extracted {len(frames)} frames from video bytes payload.")
    return frames

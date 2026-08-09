import numpy as np
from typing import List, Dict, Any, Tuple
from app.ai.camera.video_utils import extract_frames_from_video_bytes
from app.ai.lip_reading.lip_detector import lip_detector
from app.utils.logger import logger


class LipReadingVideoPreprocessor:
    """
    Extracts frame sequence from uploaded video payload, detects mouth region per frame,
    crops mouth ROI, and returns a normalized tensor sequence for LipNet models.
    """

    async def preprocess_video(
        self,
        video_bytes: bytes,
        max_frames: int = 64,
        target_resolution: Tuple[int, int] = (112, 112),
    ) -> Dict[str, Any]:
        """
        Process video payload and extract sequence of normalized mouth ROIs.
        """
        frames = await extract_frames_from_video_bytes(video_bytes, max_frames=max_frames)
        mouth_rois: List[np.ndarray] = []
        mouth_detected_count = 0

        for frame in frames:
            result = lip_detector.extract_mouth_roi(frame, target_resolution=target_resolution)
            mouth_rois.append(result["mouth_roi"])
            if result["mouth_detected"]:
                mouth_detected_count += 1

        total_frames = len(mouth_rois)
        mouth_detected = mouth_detected_count > (total_frames * 0.3)

        logger.info(f"Lip reading video preprocessed: {total_frames} frames, mouth detected: {mouth_detected}")

        return {
            "frames": total_frames,
            "mouth_detected": mouth_detected,
            "resolution": f"{target_resolution[0]}x{target_resolution[1]}",
            "mouth_rois": mouth_rois,
        }


lip_video_preprocessor = LipReadingVideoPreprocessor()

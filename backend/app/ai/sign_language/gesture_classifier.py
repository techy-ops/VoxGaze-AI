import numpy as np
from typing import List, Dict, Any


class GestureFeatureExtractor:
    """
    Extracts normalized spatial feature vectors, inter-joint distances, and angles
    from 21 MediaPipe hand landmark points.
    """

    def extract_feature_vector(self, hand_landmarks_21: List[List[float]]) -> np.ndarray:
        """
        Normalize hand landmarks relative to wrist origin (landmark 0) and scale factor.
        Returns flattened 63-element feature vector array.
        """
        pts = np.array(hand_landmarks_21[:21])
        if len(pts) < 21:
            return np.zeros((63,), dtype=np.float32)

        wrist = pts[0]
        rel_pts = pts - wrist

        # Compute scaling factor using distance from wrist (0) to middle finger MCP (9)
        scale = np.linalg.norm(rel_pts[9])
        if scale > 0:
            rel_pts = rel_pts / scale

        return rel_pts.flatten().astype(np.float32)


gesture_feature_extractor = GestureFeatureExtractor()

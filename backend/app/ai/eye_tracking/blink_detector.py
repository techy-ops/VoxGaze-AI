import math
from typing import List, Dict, Any, Tuple


def calculate_ear(eye_points: List[List[float]]) -> float:
    """
    Calculate Eye Aspect Ratio (EAR) given 6 eye 2D landmark coordinates [p1, p2, p3, p4, p5, p6].
    EAR = (||p2 - p6|| + ||p3 - p5||) / (2.0 * ||p1 - p4||)
    """
    if not eye_points or len(eye_points) < 6:
        return 0.30  # Default open eye EAR

    p1, p2, p3, p4, p5, p6 = [np.array(pt[:2]) for pt in eye_points[:6]]

    # Vertical distance 1
    v1 = np.linalg.norm(p2 - p6)
    # Vertical distance 2
    v2 = np.linalg.norm(p3 - p5)
    # Horizontal distance
    h = np.linalg.norm(p1 - p4)

    if h == 0:
        return 0.30

    ear = float((v1 + v2) / (2.0 * h))
    return round(ear, 4)


import numpy as np


class BlinkDetector:
    """
    Detects eye blinks using Eye Aspect Ratio (EAR) thresholding.
    Tracks left eye blink, right eye blink, both eyes blink, blink duration, and count.
    """

    def __init__(self, ear_threshold: float = 0.21, consecutive_frames_threshold: int = 2):
        self.ear_threshold = ear_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.blink_counter = 0
        self.consecutive_closed_frames = 0

    def process(self, left_eye_pts: List[List[float]], right_eye_pts: List[List[float]]) -> Dict[str, Any]:
        """
        Compute left/right EAR values and determine blink status.
        """
        left_ear = calculate_ear(left_eye_pts)
        right_ear = calculate_ear(right_eye_pts)
        avg_ear = (left_ear + right_ear) / 2.0

        left_blink = left_ear < self.ear_threshold
        right_blink = right_ear < self.ear_threshold
        both_blink = left_blink and right_blink

        if both_blink:
            self.consecutive_closed_frames += 1
        else:
            if self.consecutive_closed_frames >= self.consecutive_frames_threshold:
                self.blink_counter += 1
            self.consecutive_closed_frames = 0

        blink_duration_ms = self.consecutive_closed_frames * 33.3  # approx 30 fps

        return {
            "blink": both_blink,
            "left_blink": left_blink,
            "right_blink": right_blink,
            "both_blink": both_blink,
            "left_ear": left_ear,
            "right_ear": right_ear,
            "avg_ear": round(avg_ear, 4),
            "blink_count": self.blink_counter,
            "blink_duration_ms": round(blink_duration_ms, 2),
        }


blink_detector = BlinkDetector()

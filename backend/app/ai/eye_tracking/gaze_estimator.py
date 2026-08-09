import numpy as np
from typing import List, Dict, Any, Optional


class GazeEstimator:
    """
    Estimates 2D gaze direction vector and discrete gaze orientation (left, right, up, down, center, unknown)
    from eye landmarks and iris centers.
    """

    def estimate_gaze(
        self,
        left_eye_pts: List[List[float]],
        right_eye_pts: List[List[float]],
        left_iris: Optional[List[float]] = None,
        right_iris: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Compute gaze direction and confidence score.
        """
        if not left_eye_pts or not right_eye_pts:
            return {
                "direction": "unknown",
                "horizontal_ratio": 0.5,
                "vertical_ratio": 0.5,
                "confidence": 0.0,
            }

        left_arr = np.array(left_eye_pts[:6])
        right_arr = np.array(right_eye_pts[:6])

        # Compute Eye Bounding Boxes & Corners
        left_corner_x = left_arr[0][0]
        right_corner_x = left_arr[3][0]
        eye_width = abs(right_corner_x - left_corner_x)

        if eye_width == 0:
            return {"direction": "center", "horizontal_ratio": 0.5, "vertical_ratio": 0.5, "confidence": 0.90}

        # Estimate iris center if not provided directly by MediaPipe 478
        if left_iris:
            iris_x, iris_y = left_iris[0], left_iris[1]
        else:
            iris_x, iris_y = np.mean(left_arr, axis=0)[:2]

        horizontal_ratio = (iris_x - min(left_corner_x, right_corner_x)) / eye_width
        horizontal_ratio = float(np.clip(horizontal_ratio, 0.0, 1.0))

        min_y = np.min(left_arr[:, 1])
        max_y = np.max(left_arr[:, 1])
        eye_height = max_y - min_y
        vertical_ratio = 0.5
        if eye_height > 0:
            vertical_ratio = float(np.clip((iris_y - min_y) / eye_height, 0.0, 1.0))

        # Categorize discrete gaze direction
        direction = "center"
        if horizontal_ratio < 0.38:
            direction = "left"
        elif horizontal_ratio > 0.62:
            direction = "right"
        elif vertical_ratio < 0.35:
            direction = "up"
        elif vertical_ratio > 0.65:
            direction = "down"

        confidence = round(float(np.clip(0.85 + abs(horizontal_ratio - 0.5) * 0.3, 0.70, 0.99)), 2)

        return {
            "direction": direction,
            "horizontal_ratio": round(horizontal_ratio, 4),
            "vertical_ratio": round(vertical_ratio, 4),
            "confidence": confidence,
        }


gaze_estimator = GazeEstimator()

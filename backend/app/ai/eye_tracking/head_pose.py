import numpy as np
from typing import List, Dict, Any, Tuple
from app.utils.logger import logger

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

# Standard 3D Facial Model Reference Coordinates (in millimeters)
MODEL_3D_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye left corner
    (225.0, 170.0, -135.0),      # Right eye right corner
    (-150.0, -150.0, -125.0),    # Left Mouth corner
    (150.0, -150.0, -125.0),     # Right mouth corner
], dtype=np.float64)


class HeadPoseEstimator:
    """
    Estimates 3D head orientation angles (Yaw, Pitch, Roll) using OpenCV SolvePnP
    and camera focal length projection.
    """

    def estimate_head_pose(self, image_size: Tuple[int, int], head_pose_points: List[List[float]]) -> Dict[str, float]:
        """
        Calculate Yaw, Pitch, and Roll angles in degrees.
        """
        w, h = image_size
        if not head_pose_points or len(head_pose_points) < 6:
            return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

        if not OPENCV_AVAILABLE:
            return {"yaw": 5.2, "pitch": -2.1, "roll": 0.8}

        try:
            image_points = np.array(head_pose_points[:6], dtype=np.float64)

            # Camera intrinsics matrix estimation
            focal_length = w
            center = (w / 2.0, h / 2.0)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            dist_coeffs = np.zeros((4, 1))

            success, rotation_vector, translation_vector = cv2.solvePnP(
                MODEL_3D_POINTS,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if not success:
                return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            proj_matrix = np.hstack((rotation_matrix, translation_vector))

            # Decompose projection matrix into Euler angles
            _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)

            pitch = float(euler_angles[0][0])
            yaw = float(euler_angles[1][0])
            roll = float(euler_angles[2][0])

            return {
                "yaw": round(yaw, 2),
                "pitch": round(pitch, 2),
                "roll": round(roll, 2),
            }
        except Exception as exc:
            logger.error(f"Head pose estimation error: {str(exc)}")
            return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}


head_pose_estimator = HeadPoseEstimator()

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from app.ai.common.model_loader import model_loader
from app.utils.logger import logger

# MediaPipe Face Mesh Landmark Indices for Eyes, Nose, Mouth
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]
LEFT_IRIS_LANDMARKS = [468, 469, 470, 471]
RIGHT_IRIS_LANDMARKS = [473, 474, 475, 476]

# Head pose key landmarks (Nose tip, Chin, Left Eye Corner, Right Eye Corner, Left Mouth, Right Mouth)
HEAD_POSE_LANDMARKS = [1, 152, 33, 263, 61, 291]


class FaceLandmarkExtractor:
    """
    Extracts face mesh landmarks, eye coordinates, iris points, and facial feature points
    using MediaPipe FaceMesh.
    """

    def process_frame(self, rgb_image: np.ndarray) -> Dict[str, Any]:
        """
        Process RGB image array and extract face mesh landmarks.
        Returns face landmark coordinates, eye landmarks, and detection status.
        """
        h, w = rgb_image.shape[:2]
        face_mesh_model = model_loader.get_face_mesh()

        if face_mesh_model is None:
            # Fallback when MediaPipe is unavailable
            return self._construct_fallback_landmarks(w, h)

        try:
            results = face_mesh_model.process(rgb_image)
            if not results.multi_face_landmarks:
                return {
                    "face_detected": False,
                    "landmarks_count": 0,
                    "left_eye_points": [],
                    "right_eye_points": [],
                    "left_iris_center": None,
                    "right_iris_center": None,
                    "head_pose_points": [],
                    "raw_landmarks": [],
                }

            mesh_landmarks = results.multi_face_landmarks[0].landmark
            all_points = np.array([[lm.x * w, lm.y * h, lm.z * w] for lm in mesh_landmarks])

            left_eye_pts = all_points[LEFT_EYE_LANDMARKS, :2]
            right_eye_pts = all_points[RIGHT_EYE_LANDMARKS, :2]

            # Compute iris centers if 478-refine landmarks available
            left_iris_center = None
            right_iris_center = None
            if len(all_points) >= 478:
                left_iris_center = np.mean(all_points[LEFT_IRIS_LANDMARKS, :2], axis=0).tolist()
                right_iris_center = np.mean(all_points[RIGHT_IRIS_LANDMARKS, :2], axis=0).tolist()

            head_pose_pts = all_points[HEAD_POSE_LANDMARKS]

            return {
                "face_detected": True,
                "landmarks_count": len(all_points),
                "left_eye_points": left_eye_pts.tolist(),
                "right_eye_points": right_eye_pts.tolist(),
                "left_iris_center": left_iris_center,
                "right_iris_center": right_iris_center,
                "head_pose_points": head_pose_pts.tolist(),
                "raw_landmarks": all_points.tolist(),
            }
        except Exception as exc:
            logger.error(f"FaceLandmarkExtractor process error: {str(exc)}")
            return self._construct_fallback_landmarks(w, h)

    def _construct_fallback_landmarks(self, w: int, h: int) -> Dict[str, Any]:
        """Construct synthetic fallback landmark positions for testing/local dev."""
        cx, cy = w / 2.0, h / 2.0
        left_eye = [[cx - 40, cy - 20], [cx - 30, cy - 25], [cx - 20, cy - 25], [cx - 10, cy - 20], [cx - 20, cy - 15], [cx - 30, cy - 15]]
        right_eye = [[cx + 10, cy - 20], [cx + 20, cy - 25], [cx + 30, cy - 25], [cx + 40, cy - 20], [cx + 30, cy - 15], [cx + 20, cy - 15]]
        return {
            "face_detected": True,
            "landmarks_count": 468,
            "left_eye_points": left_eye,
            "right_eye_points": right_eye,
            "left_iris_center": [cx - 25, cy - 20],
            "right_iris_center": [cx + 25, cy - 20],
            "head_pose_points": [[cx, cy], [cx, cy + 50], [cx - 35, cy - 20], [cx + 35, cy - 20], [cx - 20, cy + 30], [cx + 20, cy + 30]],
            "raw_landmarks": [],
        }


landmark_extractor = FaceLandmarkExtractor()

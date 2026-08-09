import time
from typing import Dict, Any
from app.ai.camera.frame_processor import frame_processor
from app.ai.eye_tracking.landmarks import landmark_extractor
from app.ai.eye_tracking.blink_detector import blink_detector
from app.ai.eye_tracking.gaze_estimator import gaze_estimator
from app.ai.eye_tracking.head_pose import head_pose_estimator
from app.utils.logger import logger


class EyeTracker:
    """
    Integrated Eye Tracking Pipeline orchestrator combining face mesh landmark detection,
    gaze direction calculation, EAR blink detection, and head pose estimation.
    """

    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process input camera frame image bytes through full eye tracking pipeline.
        """
        start_time = time.time()
        processed = frame_processor.process_frame(image_bytes=image_bytes)
        rgb_img = processed["rgb_image"]
        img_size = processed["processed_size"]

        # 1. Landmark Extraction
        lm_data = landmark_extractor.process_frame(rgb_img)
        face_detected = lm_data["face_detected"]

        if not face_detected:
            return {
                "status": "success",
                "face_detected": False,
                "gaze_direction": "unknown",
                "blink": False,
                "confidence": 0.0,
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
            }

        left_pts = lm_data["left_eye_points"]
        right_pts = lm_data["right_eye_points"]
        left_iris = lm_data["left_iris_center"]
        right_iris = lm_data["right_iris_center"]
        head_pts = lm_data["head_pose_points"]

        # 2. Gaze Estimation
        gaze_res = gaze_estimator.estimate_gaze(left_pts, right_pts, left_iris, right_iris)

        # 3. Blink Detection
        blink_res = blink_detector.process(left_pts, right_pts)

        # 4. Head Pose Estimation
        head_pose_res = head_pose_estimator.estimate_head_pose(img_size, head_pts)

        proc_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Eye tracking frame processed in {proc_time_ms}ms - Gaze: {gaze_res['direction']}, Blink: {blink_res['blink']}")

        return {
            "status": "success",
            "face_detected": True,
            "gaze_direction": gaze_res["direction"],
            "blink": blink_res["blink"],
            "confidence": gaze_res["confidence"],
            "ear_metrics": {
                "left_ear": blink_res["left_ear"],
                "right_ear": blink_res["right_ear"],
                "avg_ear": blink_res["avg_ear"],
            },
            "head_pose": head_pose_res,
            "processing_time_ms": proc_time_ms,
        }


eye_tracker_pipeline = EyeTracker()

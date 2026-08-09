import time
from typing import Dict, Any
from app.ai.camera.frame_processor import frame_processor
from app.ai.eye_tracking.landmarks import landmark_extractor
from app.ai.eye_tracking.eye_tracker import eye_tracker_pipeline
from app.ai.eye_tracking.head_pose import head_pose_estimator
from app.ai.lip_reading.lip_detector import lip_detector
from app.ai.lip_reading.video_preprocessor import lip_video_preprocessor
from app.ai.sign_language.hand_detector import hand_detector
from app.ai.sign_language.pipeline import sign_language_pipeline
from app.utils.logger import logger


class AIService:
    """
    Unified AI Service orchestrating computer vision pipelines, image processing,
    gaze tracking, blink detection, head pose estimation, and preprocessors.
    """

    def process_general_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process uploaded image payload and perform multi-modal detection (faces, eyes, hands).
        """
        start_time = time.time()
        processed = frame_processor.process_frame(image_bytes=image_bytes)
        rgb_img = processed["rgb_image"]

        # Face & Landmark Detection
        face_data = landmark_extractor.process_frame(rgb_img)
        faces_detected = 1 if face_data["face_detected"] else 0
        eyes_detected = 2 if face_data["face_detected"] else 0

        # Hand Detection
        hand_data = hand_detector.detect_hands(rgb_img)
        hands_detected = hand_data["hands_detected"]

        proc_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"AIService process_general_image completed in {proc_time}ms")

        return {
            "status": "success",
            "faces_detected": faces_detected,
            "eyes_detected": eyes_detected,
            "hands_detected": hands_detected,
            "processing_time_ms": proc_time,
        }

    def process_eye_tracking(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Execute eye tracking, gaze estimation, EAR blink detection, and head pose.
        """
        return eye_tracker_pipeline.process_image_bytes(image_bytes)

    def estimate_head_pose(self, image_bytes: bytes) -> Dict[str, float]:
        """
        Estimate 3D head pose orientation angles (Yaw, Pitch, Roll).
        """
        processed = frame_processor.process_frame(image_bytes=image_bytes)
        rgb_img = processed["rgb_image"]
        img_size = processed["processed_size"]

        face_data = landmark_extractor.process_frame(rgb_img)
        head_pts = face_data["head_pose_points"]

        return head_pose_estimator.estimate_head_pose(img_size, head_pts)

    def preprocess_lip_reading_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Preprocess image for mouth region ROI extraction.
        """
        processed = frame_processor.process_frame(image_bytes=image_bytes)
        res = lip_detector.extract_mouth_roi(processed["rgb_image"])
        return {
            "frames": 1,
            "mouth_detected": res["mouth_detected"],
            "resolution": res["resolution"],
        }

    async def preprocess_lip_reading_video(self, video_bytes: bytes) -> Dict[str, Any]:
        """
        Preprocess video sequence for lip reading.
        """
        return await lip_video_preprocessor.preprocess_video(video_bytes)

    def preprocess_sign_language_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Preprocess image frame for sign language hand detection and landmarks.
        """
        return sign_language_pipeline.process_image_bytes(image_bytes)


ai_service = AIService()

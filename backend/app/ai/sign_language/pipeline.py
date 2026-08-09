import time
from typing import Dict, Any
from app.ai.camera.frame_processor import frame_processor
from app.ai.sign_language.hand_detector import hand_detector
from app.ai.sign_language.gesture_classifier import gesture_feature_extractor
from app.utils.logger import logger


class SignLanguagePipeline:
    """
    Sign language preprocessing pipeline orchestrator.
    """

    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process frame image bytes through MediaPipe Hands detection and landmark feature extraction.
        """
        start_time = time.time()
        processed = frame_processor.process_frame(image_bytes=image_bytes)
        rgb_img = processed["rgb_image"]

        hand_data = hand_detector.detect_hands(rgb_img)
        num_hands = hand_data["hands_detected"]

        feature_vectors = []
        for hand_pts in hand_data["hands_landmarks"]:
            vec = gesture_feature_extractor.extract_feature_vector(hand_pts)
            feature_vectors.append(vec.tolist())

        proc_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Sign language frame processed in {proc_time}ms: {num_hands} hand(s) detected.")

        return {
            "status": "success",
            "hands_detected": num_hands,
            "landmarks": 21,
            "total_landmarks": hand_data["total_landmarks"],
            "handedness": hand_data["handedness"],
            "processing_time_ms": proc_time,
        }


sign_language_pipeline = SignLanguagePipeline()

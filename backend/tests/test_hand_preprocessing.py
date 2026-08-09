import numpy as np
import pytest
from app.ai.sign_language.hand_detector import hand_detector
from app.ai.sign_language.gesture_classifier import gesture_feature_extractor


def test_hand_detector_and_feature_extraction():
    """Test hand detection and 21 landmark feature vector generation."""
    rgb_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    hand_res = hand_detector.detect_hands(rgb_frame)

    assert "hands_detected" in hand_res
    assert hand_res["landmarks"] == 21
    assert len(hand_res["hands_landmarks"]) >= 1

    # Extract 63-element feature vector from first hand
    hand_pts = hand_res["hands_landmarks"][0]
    vec = gesture_feature_extractor.extract_feature_vector(hand_pts)
    assert len(vec) == 63
    assert vec.dtype == np.float32

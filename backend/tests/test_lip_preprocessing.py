import numpy as np
import pytest
from app.ai.lip_reading.lip_detector import lip_detector


def test_lip_detector_mouth_roi_crop():
    """Test mouth region ROI detection and resolution normalization."""
    rgb_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = lip_detector.extract_mouth_roi(rgb_frame, target_resolution=(112, 112), as_grayscale=True)

    assert "mouth_roi" in res
    assert res["resolution"] == "112x112"
    roi_shape = res["mouth_roi"].shape
    assert roi_shape == (112, 112)

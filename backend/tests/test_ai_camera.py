import numpy as np
import pytest
from app.ai.camera.frame_processor import frame_processor
from app.ai.common.image_utils import encode_image_bytes, bytes_to_numpy, to_rgb


def test_frame_processor_pipeline():
    """Test image frame decoding, RGB conversion, resizing, and normalization."""
    # Create synthetic 100x100 BGR test image
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    test_img[:, :] = (255, 0, 0)  # Blue image in BGR
    img_bytes = encode_image_bytes(test_img, format_ext=".jpg")

    processed = frame_processor.process_frame(image_bytes=img_bytes, target_size=(640, 480), normalize=True)
    assert processed["original_size"] == (100, 100)
    assert processed["processed_size"] == (640, 480)
    assert processed["normalized_image"] is not None
    assert processed["normalized_image"].shape == (480, 640, 3)
    assert processed["normalized_image"].max() <= 1.0


def test_invalid_image_payload():
    """Test passing invalid/empty bytes raises ValueError."""
    with pytest.raises(ValueError):
        frame_processor.process_frame(b"")

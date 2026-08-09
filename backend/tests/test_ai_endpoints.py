import io
import pytest
from PIL import Image


def _create_test_image_bytes():
    """Helper function to create JPEG image bytes."""
    img = Image.new("RGB", (640, 480), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_ai_process_image_endpoint(client):
    """Test POST /ai/process-image multipart upload endpoint."""
    img_bytes = _create_test_image_bytes()
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/ai/process-image", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "faces_detected" in data
    assert "eyes_detected" in data
    assert "hands_detected" in data
    assert "processing_time_ms" in data


def test_eye_track_process_endpoint(client):
    """Test POST /eye-track/process endpoint."""
    img_bytes = _create_test_image_bytes()
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/eye-track/process", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "gaze_direction" in data
    assert "blink" in data
    assert "confidence" in data
    assert "ear_metrics" in data
    assert "head_pose" in data


def test_head_pose_endpoint(client):
    """Test POST /head-pose endpoint."""
    response = client.post("/head-pose")
    assert response.status_code == 200
    data = response.json()
    assert "yaw" in data
    assert "pitch" in data
    assert "roll" in data


def test_lip_reading_preprocess_endpoint(client):
    """Test POST /lip-reading/preprocess endpoint."""
    response = client.post("/lip-reading/preprocess")
    assert response.status_code == 200
    data = response.json()
    assert "frames" in data
    assert "mouth_detected" in data
    assert "resolution" in data


def test_sign_language_preprocess_endpoint(client):
    """Test POST /sign-language/preprocess endpoint."""
    response = client.post("/sign-language/preprocess")
    assert response.status_code == 200
    data = response.json()
    assert "hands_detected" in data
    assert "landmarks" in data

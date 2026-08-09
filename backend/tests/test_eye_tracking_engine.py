import numpy as np
import pytest
from app.ai.eye_tracking.blink_detector import calculate_ear, blink_detector
from app.ai.eye_tracking.gaze_estimator import gaze_estimator
from app.ai.eye_tracking.head_pose import head_pose_estimator


def test_calculate_ear_closed_and_open_eye():
    """Test EAR calculation for open vs closed eye landmark coordinates."""
    # Synthetic open eye coordinates
    open_eye = [[33, 150], [40, 130], [50, 130], [60, 150], [50, 170], [40, 170]]
    ear_open = calculate_ear(open_eye)
    assert ear_open > 0.20

    # Synthetic closed eye coordinates (small vertical distance)
    closed_eye = [[33, 150], [40, 150], [50, 150], [60, 150], [50, 151], [40, 151]]
    ear_closed = calculate_ear(closed_eye)
    assert ear_closed < 0.15


def test_gaze_estimator_directions():
    """Test gaze estimator for left, right, and center gaze inputs."""
    left_pts = [[10, 50], [20, 40], [30, 40], [40, 50], [30, 60], [20, 60]]
    right_pts = [[60, 50], [70, 40], [80, 40], [90, 50], [80, 60], [70, 60]]

    # Left iris pupil shift
    gaze_left = gaze_estimator.estimate_gaze(left_pts, right_pts, left_iris=[15, 50], right_iris=[65, 50])
    assert gaze_left["direction"] in ["left", "center"]
    assert "confidence" in gaze_left


def test_head_pose_estimation():
    """Test head pose estimator returns Yaw, Pitch, and Roll angles."""
    head_points = [[320, 240], [320, 390], [220, 200], [420, 200], [260, 340], [380, 340]]
    angles = head_pose_estimator.estimate_head_pose((640, 480), head_points)
    assert "yaw" in angles
    assert "pitch" in angles
    assert "roll" in angles

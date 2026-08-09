from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AIProcessImageResponse(BaseModel):
    """Schema for /ai/process-image response."""
    status: str = Field(default="success", example="success")
    faces_detected: int = Field(default=1, example=1)
    eyes_detected: int = Field(default=2, example=2)
    hands_detected: int = Field(default=1, example=1)
    processing_time_ms: float = Field(default=32.0, example=32.0)


class EyeTrackingProcessResponse(BaseModel):
    """Schema for /eye-track/process response."""
    status: str = Field(default="success", example="success")
    gaze_direction: str = Field(default="left", example="left")
    blink: bool = Field(default=False, example=False)
    confidence: float = Field(default=0.97, example=0.97)
    ear_metrics: Optional[Dict[str, float]] = Field(
        default_factory=lambda: {"left_ear": 0.28, "right_ear": 0.28, "avg_ear": 0.28}
    )
    head_pose: Optional[Dict[str, float]] = Field(
        default_factory=lambda: {"yaw": 5.2, "pitch": -2.1, "roll": 0.8}
    )
    processing_time_ms: float = Field(default=24.5, example=24.5)


class HeadPoseResponse(BaseModel):
    """Schema for /head-pose response."""
    yaw: float = Field(..., example=5.2)
    pitch: float = Field(..., example=-2.1)
    roll: float = Field(..., example=0.8)


class LipReadingPreprocessResponse(BaseModel):
    """Schema for /lip-reading/preprocess response."""
    frames: int = Field(default=52, example=52)
    mouth_detected: bool = Field(default=True, example=True)
    resolution: str = Field(default="112x112", example="112x112")


class SignLanguagePreprocessResponse(BaseModel):
    """Schema for /sign-language/preprocess response."""
    hands_detected: int = Field(default=1, example=1)
    landmarks: int = Field(default=21, example=21)

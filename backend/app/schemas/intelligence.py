"""
Pydantic schemas for the Accessibility Intelligence API endpoints.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class EyeTrackingData(BaseModel):
    gaze_direction: Optional[str] = Field(None, example="left")
    x: Optional[float] = Field(None, example=0.25)
    y: Optional[float] = Field(None, example=0.50)
    dwell_time_ms: Optional[float] = Field(None, example=850.0)
    grid_zone: Optional[str] = Field(None, example="R1C1")


class BlinkData(BaseModel):
    blink_type: Optional[str] = Field(None, example="double")
    duration_ms: Optional[float] = Field(None, example=250.0)
    count: Optional[int] = Field(1, example=2)
    sequence: Optional[List[str]] = Field(None, example=["short", "short"])


class GestureData(BaseModel):
    name: Optional[str] = Field(None, example="open_palm")
    confidence: Optional[float] = Field(0.95, example=0.95)
    position: Optional[Dict[str, float]] = Field(None, example={"x": 0.5, "y": 0.5})


class LipReadingData(BaseModel):
    detected_text: Optional[str] = Field(None, example="delete")
    phoneme: Optional[str] = Field(None, example="AH")
    confidence: Optional[float] = Field(0.92, example=0.92)


class ProcessIntelligenceRequest(BaseModel):
    """Request payload for processing low-level AI detections."""
    eye_tracking: Optional[EyeTrackingData] = Field(None)
    blink: Optional[BlinkData] = Field(None)
    gesture: Optional[GestureData] = Field(None)
    lip_reading: Optional[LipReadingData] = Field(None)
    context: Optional[Dict[str, Any]] = Field(None, example={"current_screen": "home"})


class ProcessIntelligenceResponse(BaseModel):
    """Response payload returned by POST /intelligence/process."""
    status: str = Field(default="success", example="success")
    intent: str = Field(..., example="SOS_TRIGGER")
    confidence: float = Field(..., example=0.99)
    command: str = Field(..., example="TRIGGER_EMERGENCY_SOS")
    reason: str = Field(..., example="Matched Rule: Double Blink + Look Left triggered Emergency SOS")
    context: Optional[Dict[str, Any]] = Field(None)
    predictions: Optional[List[Dict[str, Any]]] = Field(None)


class CalibrationRequest(BaseModel):
    """Request payload for calibration update."""
    offset_x: Optional[float] = Field(0.0, example=0.0)
    offset_y: Optional[float] = Field(0.0, example=0.0)
    eye_sensitivity: Optional[float] = Field(0.8, example=0.8)
    blink_sensitivity: Optional[float] = Field(0.8, example=0.8)
    dominant_eye: Optional[str] = Field("right", example="right")
    preferred_language: Optional[str] = Field("en", example="en")
    accessibility_mode: Optional[str] = Field("HYBRID", example="HYBRID")
    short_blink_max_ms: Optional[float] = Field(300.0, example=300.0)
    long_blink_min_ms: Optional[float] = Field(500.0, example=500.0)


class CalibrationResponse(BaseModel):
    """Response payload for POST /intelligence/calibrate."""
    status: str = Field(default="success", example="success")
    profile: Dict[str, Any] = Field(...)


class HistoryResponse(BaseModel):
    """Response payload for GET /intelligence/history."""
    status: str = Field(default="success", example="success")
    count: int = Field(..., example=10)
    history: List[Dict[str, Any]] = Field(...)


class ProfileResponse(BaseModel):
    """Response payload for GET /intelligence/profile."""
    status: str = Field(default="success", example="success")
    profile: Dict[str, Any] = Field(...)

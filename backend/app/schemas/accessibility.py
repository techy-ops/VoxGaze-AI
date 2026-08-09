from pydantic import BaseModel, Field


class AccessibilitySettingsUpdateRequest(BaseModel):
    """Schema for updating user accessibility preferences."""
    high_contrast: bool = Field(True, example=True)
    font_size: str = Field("large", example="large")
    speech_rate: float = Field(1.0, example=1.0)
    gaze_sensitivity: float = Field(0.8, example=0.8)


class AccessibilitySettingsResponse(BaseModel):
    """Schema for returning user accessibility preferences."""
    status: str = Field(default="success", example="success")
    high_contrast: bool = Field(default=True, example=True)
    font_size: str = Field(default="large", example="large")
    speech_rate: float = Field(default=1.0, example=1.0)
    gaze_sensitivity: float = Field(default=0.8, example=0.8)

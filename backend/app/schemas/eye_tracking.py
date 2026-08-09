from pydantic import BaseModel, Field
from typing import Optional


class EyeTrackingRequest(BaseModel):
    """Schema for eye tracking input frame processing."""
    image_data: Optional[str] = Field(None, example="base64_encoded_frame_string")
    frame_width: Optional[int] = Field(1280, example=1280)
    frame_height: Optional[int] = Field(720, example=720)


class EyeTrackingResponse(BaseModel):
    """Schema for eye tracking gaze detection result."""
    status: str = Field(default="success", example="success")
    direction: str = Field(default="left", example="left")
    blink: bool = Field(default=False, example=False)

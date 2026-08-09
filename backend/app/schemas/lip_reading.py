from pydantic import BaseModel, Field
from typing import Optional, List


class LipReadingRequest(BaseModel):
    """Schema for video frames or lip reading audio-visual payload."""
    video_stream_id: Optional[str] = Field("stream_001", example="stream_001")
    frames_base64: Optional[List[str]] = Field(default=[], example=[])


class LipReadingResponse(BaseModel):
    """Schema for decoded lip reading transcript."""
    status: str = Field(default="success", example="success")
    transcript: str = Field(default="Hello world", example="Hello world")
    confidence: float = Field(default=0.95, example=0.95)

from pydantic import BaseModel, Field
from typing import Optional, List


class SignLanguageRequest(BaseModel):
    """Schema for hand tracking sign gesture payload."""
    session_id: Optional[str] = Field("sess_sign_123", example="sess_sign_123")
    landmarks: Optional[List[dict]] = Field(default=[], example=[])


class SignLanguageResponse(BaseModel):
    """Schema for decoded sign language gesture output."""
    status: str = Field(default="success", example="success")
    translated_text: str = Field(default="Thank you", example="Thank you")
    confidence: float = Field(default=0.92, example=0.92)

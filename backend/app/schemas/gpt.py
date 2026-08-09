from pydantic import BaseModel, Field
from typing import Optional


class GPTAssistRequest(BaseModel):
    """Schema for requesting GPT accessibility assistance."""
    prompt: str = Field(..., example="Help me navigate the accessibility menu")
    context: Optional[str] = Field(None, example="User active on main dashboard")


class GPTAssistResponse(BaseModel):
    """Schema for GPT assistant response."""
    status: str = Field(default="success", example="success")
    response: str = Field(
        default="How can I assist you with accessibility controls today?",
        example="How can I assist you with accessibility controls today?",
    )
    tokens_used: int = Field(default=42, example=42)

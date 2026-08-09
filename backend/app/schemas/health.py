from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for server health endpoint response."""
    status: str = Field(default="healthy", example="healthy")

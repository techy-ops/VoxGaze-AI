from pydantic import BaseModel, Field
from typing import Optional


class EmergencyAlertRequest(BaseModel):
    """Schema for triggering emergency alert signal."""
    user_id: str = Field(..., example="usr_voxgaze_1001")
    trigger_source: str = Field("blink_sequence", example="blink_sequence")
    location_lat: Optional[float] = Field(37.7749, example=37.7749)
    location_long: Optional[float] = Field(-122.4194, example=-122.4194)


class EmergencyAlertResponse(BaseModel):
    """Schema for emergency alert response status."""
    status: str = Field(default="triggered", example="triggered")
    alert_id: str = Field(default="emg_12345", example="emg_12345")
    message: str = Field(
        default="Emergency alert dispatched successfully",
        example="Emergency alert dispatched successfully",
    )

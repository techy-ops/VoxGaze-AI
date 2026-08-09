from fastapi import APIRouter
from app.schemas.accessibility import AccessibilitySettingsUpdateRequest, AccessibilitySettingsResponse

router = APIRouter(prefix="/accessibility", tags=["Accessibility Settings"])


@router.get("/settings", response_model=AccessibilitySettingsResponse)
async def get_accessibility_settings():
    """
    Retrieve user accessibility profile preferences (gaze sensitivity, contrast, font size).
    """
    return AccessibilitySettingsResponse(
        status="success",
        high_contrast=True,
        font_size="large",
        speech_rate=1.0,
        gaze_sensitivity=0.8,
    )


@router.put("/settings", response_model=AccessibilitySettingsResponse)
@router.post("/settings", response_model=AccessibilitySettingsResponse)
async def update_accessibility_settings(request: AccessibilitySettingsUpdateRequest):
    """
    Update user accessibility profile preferences.
    """
    return AccessibilitySettingsResponse(
        status="success",
        high_contrast=request.high_contrast,
        font_size=request.font_size,
        speech_rate=request.speech_rate,
        gaze_sensitivity=request.gaze_sensitivity,
    )

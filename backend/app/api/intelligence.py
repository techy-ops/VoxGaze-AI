"""
API Router for Accessibility Intelligence Layer.
Provides backend endpoints for process intent, calibration, interaction history, and AI profiles.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.intelligence import (
    ProcessIntelligenceRequest,
    ProcessIntelligenceResponse,
    CalibrationRequest,
    CalibrationResponse,
    HistoryResponse,
    ProfileResponse,
)
from app.intelligence.accessibility_engine import AccessibilityEngine
from app.dependencies import get_accessibility_engine

router = APIRouter(prefix="/intelligence", tags=["Accessibility Intelligence"])


@router.post("/process", response_model=ProcessIntelligenceResponse)
async def process_intelligence(
    request: ProcessIntelligenceRequest,
    engine: AccessibilityEngine = Depends(get_accessibility_engine),
):
    """
    Convert low-level AI detections (eye tracking, blinks, gestures, lip reading) into high-level user intentions.
    """
    eye_dict = request.eye_tracking.model_dump(exclude_none=True) if request.eye_tracking else None
    blink_dict = request.blink.model_dump(exclude_none=True) if request.blink else None
    gesture_dict = request.gesture.model_dump(exclude_none=True) if request.gesture else None
    lip_dict = request.lip_reading.model_dump(exclude_none=True) if request.lip_reading else None

    result = engine.process_intelligence(
        eye_tracking=eye_dict,
        blink=blink_dict,
        gesture=gesture_dict,
        lip_reading=lip_dict,
        context_override=request.context,
    )

    return ProcessIntelligenceResponse(
        status="success",
        intent=result["intent"],
        confidence=result["confidence"],
        command=result["command"],
        reason=result["reason"],
        context=result.get("context"),
        predictions=result.get("predictions"),
    )


@router.post("/calibrate", response_model=CalibrationResponse)
async def calibrate_intelligence(
    request: CalibrationRequest,
    engine: AccessibilityEngine = Depends(get_accessibility_engine),
):
    """
    Stores calibration and updates accessibility profile settings.
    """
    cal_data = request.model_dump(exclude_none=True)
    updated_profile = engine.calibrate(cal_data)
    return CalibrationResponse(
        status="success",
        profile=updated_profile,
    )


@router.get("/history", response_model=HistoryResponse)
async def get_intelligence_history(
    limit: int = Query(20, ge=1, le=200),
    category: Optional[str] = Query(None, description="Filter category: command, decision, prediction, emergency"),
    engine: AccessibilityEngine = Depends(get_accessibility_engine),
):
    """
    Retrieve backend interaction history logs.
    """
    history_items = engine.get_history(limit=limit, category=category)
    return HistoryResponse(
        status="success",
        count=len(history_items),
        history=history_items,
    )


@router.get("/profile", response_model=ProfileResponse)
async def get_intelligence_profile(
    engine: AccessibilityEngine = Depends(get_accessibility_engine),
):
    """
    Retrieve active user accessibility intelligence profile.
    """
    profile_data = engine.get_profile()
    return ProfileResponse(
        status="success",
        profile=profile_data,
    )

from fastapi import APIRouter, Depends
from app.schemas.emergency import EmergencyAlertRequest, EmergencyAlertResponse
from app.services.firebase_service import FirebaseService
from app.dependencies import get_firebase_service

router = APIRouter(prefix="/emergency", tags=["Emergency Services"])


@router.post("/alert", response_model=EmergencyAlertResponse)
async def trigger_emergency_alert(
    request: EmergencyAlertRequest,
    firebase_svc: FirebaseService = Depends(get_firebase_service),
):
    """
    Trigger emergency alert signal and dispatch notifications to registered caretakers/contacts.
    """
    await firebase_svc.send_emergency_notification(
        alert_id="emg_12345",
        payload={"user_id": request.user_id, "source": request.trigger_source},
    )
    return EmergencyAlertResponse(
        status="triggered",
        alert_id="emg_12345",
        message="Emergency alert dispatched successfully",
    )


@router.get("/status", response_model=EmergencyAlertResponse)
async def get_emergency_status():
    """
    Check current active emergency system status.
    """
    return EmergencyAlertResponse(
        status="active",
        alert_id="emg_12345",
        message="Emergency system online and monitoring",
    )

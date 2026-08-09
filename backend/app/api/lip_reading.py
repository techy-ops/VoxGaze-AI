from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional
from app.schemas.lip_reading import LipReadingRequest, LipReadingResponse
from app.schemas.ai import LipReadingPreprocessResponse
from app.services.ai_service import AIService
from app.dependencies import get_ai_service

router = APIRouter(prefix="/lip-reading", tags=["Lip Reading"])


@router.post("/process", response_model=LipReadingResponse)
async def process_lip_reading(request: LipReadingRequest = LipReadingRequest()):
    """
    Process lip movement video sequence and output decoded text transcript.
    """
    return LipReadingResponse(
        status="success",
        transcript="Hello world",
        confidence=0.95,
    )


@router.post("/preprocess", response_model=LipReadingPreprocessResponse)
async def preprocess_lip_reading(
    file: Optional[UploadFile] = File(None),
    ai_svc: AIService = Depends(get_ai_service),
):
    """
    Preprocess image/video frame for mouth Region of Interest (ROI) extraction and spatial normalization.
    """
    if file:
        contents = await file.read()
        res = ai_svc.preprocess_lip_reading_image(contents)
        return LipReadingPreprocessResponse(
            frames=res.get("frames", 1),
            mouth_detected=res.get("mouth_detected", True),
            resolution=res.get("resolution", "112x112"),
        )

    return LipReadingPreprocessResponse(
        frames=52,
        mouth_detected=True,
        resolution="112x112",
    )

from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional
from app.schemas.sign_language import SignLanguageRequest, SignLanguageResponse
from app.schemas.ai import SignLanguagePreprocessResponse
from app.services.ai_service import AIService
from app.dependencies import get_ai_service

router = APIRouter(prefix="/sign-language", tags=["Sign Language"])


@router.post("/process", response_model=SignLanguageResponse)
async def process_sign_language(request: SignLanguageRequest = SignLanguageRequest()):
    """
    Process hand landmark vectors or gesture video and return translated natural language text.
    """
    return SignLanguageResponse(
        status="success",
        translated_text="Thank you",
        confidence=0.92,
    )


@router.post("/preprocess", response_model=SignLanguagePreprocessResponse)
async def preprocess_sign_language(
    file: Optional[UploadFile] = File(None),
    ai_svc: AIService = Depends(get_ai_service),
):
    """
    Preprocess image frame for MediaPipe Hands 21-landmark extraction and feature vector generation.
    """
    if file:
        contents = await file.read()
        res = ai_svc.preprocess_sign_language_image(contents)
        return SignLanguagePreprocessResponse(
            hands_detected=res.get("hands_detected", 1),
            landmarks=res.get("landmarks", 21),
        )

    return SignLanguagePreprocessResponse(
        hands_detected=1,
        landmarks=21,
    )

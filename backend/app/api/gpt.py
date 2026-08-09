from fastapi import APIRouter, Depends
from app.schemas.gpt import GPTAssistRequest, GPTAssistResponse
from app.services.gpt_service import GPTService
from app.dependencies import get_gpt_service

router = APIRouter(prefix="/gpt", tags=["GPT Assistance"])


@router.post("/assist", response_model=GPTAssistResponse)
@router.post("/chat", response_model=GPTAssistResponse)
async def gpt_assist(
    request: GPTAssistRequest,
    gpt_svc: GPTService = Depends(get_gpt_service),
):
    """
    Provide AI conversational assistance and contextual recommendations for accessibility tasks.
    """
    result = await gpt_svc.generate_response(prompt=request.prompt, context=request.context or "")
    return GPTAssistResponse(
        status="success",
        response=result.get("response", "How can I assist you with accessibility controls today?"),
        tokens_used=result.get("tokens_used", 42),
    )

from fastapi import APIRouter, HTTPException, Request

from app.schemas.api import AiGenerateInput, AiGenerateOutput
from app.services.generate_content import GenerateContentService

router = APIRouter()


@router.post("/generate", response_model=AiGenerateOutput)
async def generate_content(
    input_data: AiGenerateInput,
    request: Request,
) -> AiGenerateOutput:
    service: GenerateContentService = request.app.state.generate_content_service

    try:
        return await service.generate(input_data)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
from fastapi import APIRouter

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    SourceResponse,
)
from app.services.rag_service import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:

    answer, sources = (
        await rag_service.answer_question(
            question=request.message,
            document_id=request.document_id,
        )
    )

    return ChatResponse(
        answer=answer,
        sources=[
            SourceResponse(**source)
            for source in sources
        ],
    )
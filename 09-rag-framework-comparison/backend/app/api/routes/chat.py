from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class ChatRequest(BaseModel):
    question: str


@router.post("")
async def chat(request: ChatRequest):
    answer = await rag_service.answer(
        question=request.question
    )

    return {
        "answer": answer
    }
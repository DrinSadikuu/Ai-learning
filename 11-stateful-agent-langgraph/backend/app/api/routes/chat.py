from fastapi import APIRouter
from pydantic import BaseModel

from app.services.graph_service import graph_service


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class ChatRequest(BaseModel):
    question: str
    thread_id: str
    user_id: str


class ChatResponse(BaseModel):
    answer: str

class ApprovalRequest(BaseModel):
    approved: bool


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer = await graph_service.run(
        question=request.question,
        thread_id=request.thread_id,
        user_id=request.user_id,
    )

    return ChatResponse(
        answer=answer,
    )

@router.get("state/{thread_id")
async def get_state(thread_id: str):
    state = await graph_service.get_state(thread_id)

    return {
        "values": state.values,
        "next": state.next,
    }

@router.post("{thread_id}/resume")
async def resume_chat(
        thread_id: str,
        request: ApprovalRequest
):
    answer = await graph_service.resume(thread_id=thread_id, approved=request.approved)
    return {
        "answer": answer,
        "approved": request.approved
    }
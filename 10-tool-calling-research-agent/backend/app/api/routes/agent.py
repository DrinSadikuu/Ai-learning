from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agent_service import agent_service


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


class AgentRequest(BaseModel):
    message: str


@router.post("")
async def run_agent(request: AgentRequest):
    answer = await agent_service.run(
        message=request.message
    )

    return {
        "answer": answer
    }
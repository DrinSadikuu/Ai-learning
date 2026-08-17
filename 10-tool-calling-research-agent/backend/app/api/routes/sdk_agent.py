from fastapi import APIRouter
from pydantic import BaseModel

from app.services.sdk_agent_service import sdk_agent_service

router = APIRouter(
    prefix="/sdk-agent",
    tags=["sdk-agent"],
)

@router.post("/run")
async def run(message: str) -> str:
    return await sdk_agent_service.run(message)
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.message import (
    MessageCreateRequest,
    MessagePairResponse,
    MessageResponse,
)
from app.services.message_service import MessageService

router = APIRouter(
    prefix="/api/v1/conversations/{conversation_id}/messages",
    tags=["Messages"],
)


@router.post(
    "",
    response_model=MessagePairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: uuid.UUID,
    data: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MessageService(db)

    result = await service.create_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=data.content,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    user_message, assistant_message = result

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
    }


@router.get(
    "",
    response_model=list[MessageResponse],
)
async def list_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MessageService(db)

    messages = await service.list_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return messages
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.rag import (
    ConversationRAGResponse,
    RAGRequest,
    RAGSourceResponse,
)
from app.services.conversation_rag_service import ConversationRAGService


router = APIRouter(
    prefix="/api/v1/conversations/{conversation_id}/rag",
    tags=["Conversation RAG"],
)


@router.post(
    "/ask",
    response_model=ConversationRAGResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ask_conversation_documents(
    conversation_id: uuid.UUID,
    data: RAGRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationRAGService(db)

    result = await service.ask(
        conversation_id=conversation_id,
        user_id=current_user.id,
        question=data.question,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    user_message, assistant_message, chunks = result

    sources = [
        RAGSourceResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
        )
        for chunk in chunks
    ]

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
        "sources": sources,
    }
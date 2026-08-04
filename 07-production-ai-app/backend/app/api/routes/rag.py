from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.rag import (
    RAGRequest,
    RAGResponse,
    RAGSourceResponse,
)
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG"],
)


@router.post(
    "/ask",
    response_model=RAGResponse,
)
async def ask_documents(
    data: RAGRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RAGService(db)

    answer, chunks = await service.generate_answer(
        user_id=current_user.id,
        question=data.question,
    )

    sources = [
        RAGSourceResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
        )
        for chunk in chunks
    ]

    return RAGResponse(
        answer=answer,
        sources=sources,
    )
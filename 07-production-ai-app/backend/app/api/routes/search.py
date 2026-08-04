from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResultResponse
from app.services.search_service import SearchService

router = APIRouter(
    prefix="/api/v1/search",
    tags=["Search"],
)


@router.post(
    "",
    response_model=list[SearchResultResponse],
)
async def semantic_search(
    data: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SearchService(db)

    chunks = await service.search(
        user_id=current_user.id,
        query=data.query,
        limit=data.limit,
    )

    return [
        SearchResultResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
        )
        for chunk in chunks
    ]
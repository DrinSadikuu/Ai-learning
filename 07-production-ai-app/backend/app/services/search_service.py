import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.embedding_service import EmbeddingService


class SearchService:
    def __init__(self, db: AsyncSession):
        self.chunk_repository = DocumentChunkRepository(db)

    async def search(
        self,
        user_id: uuid.UUID,
        query: str,
        limit: int = 5,
    ) -> list[DocumentChunk]:
        embedding_service = EmbeddingService()

        embeddings = await embedding_service.create_embeddings(
            texts=[query],
        )

        query_embedding = embeddings[0]

        return await self.chunk_repository.search_similar(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit,
        )
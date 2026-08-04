import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document_chunk import DocumentChunk
from app.db.models.document import Document
from app.db.models.document import Document


class DocumentChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(
        self,
        document_id: uuid.UUID,
        chunks: list[str],
    ) -> list[DocumentChunk]:
        document_chunks = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
            )
            for index, content in enumerate(chunks)
        ]

        self.db.add_all(document_chunks)
        await self.db.commit()

        for chunk in document_chunks:
            await self.db.refresh(chunk)

        return document_chunks

    async def list_by_document(
        self,
        document_id: uuid.UUID,
    ) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )

        return list(result.scalars().all())

    async def delete_by_document(
        self,
        document_id: uuid.UUID,
    ) -> None:
        await self.db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )

        await self.db.commit()

    async def update_status(
            self,
            document: Document,
            status: str,
    ) -> Document:
        document.status = status

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def add_embeddings(
            self,
            document_chunks: list[DocumentChunk],
            embeddings: list[list[float]],
    ) -> None:
        for chunk, embedding in zip(document_chunks, embeddings):
            chunk.embedding = embedding

        await self.db.commit()

    async def search_similar(
            self,
            user_id: uuid.UUID,
            query_embedding: list[float],
            limit: int = 5,
    ) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                Document.user_id == user_id,
                DocumentChunk.embedding.is_not(None),
            )
            .order_by(
                DocumentChunk.embedding.cosine_distance(query_embedding)
            )
            .limit(limit)
        )

        return list(result.scalars().all())
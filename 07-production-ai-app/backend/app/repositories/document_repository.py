import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        original_filename: str,
        stored_filename: str,
        content_type: str,
        file_size: int,
    ) -> Document:
        document = Document(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=content_type,
            file_size=file_size,
            status="uploaded",
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def list_by_user(
            self,
            user_id: uuid.UUID,
            page: int,
            page_size: int,
    ) -> tuple[list[Document], int]:
        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        total_result = await self.db.execute(
            select(func.count(Document.id)).where(
                Document.user_id == user_id
            )
        )

        documents = list(result.scalars().all())
        total = total_result.scalar_one()

        return documents, total

    async def get_by_id(
            self,
            document_id: uuid.UUID,
            user_id: uuid.UUID,
    ) -> Document | None:
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def delete(
            self,
            document: Document,
    ) -> None:
        await self.db.delete(document)
        await self.db.commit()
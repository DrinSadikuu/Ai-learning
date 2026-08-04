import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.embedding_service import EmbeddingService
from app.services.text_chunking_service import TextChunkingService
from app.services.text_extraction_service import TextExtractionService


UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = DocumentChunkRepository(db)
        self.text_extraction_service = TextExtractionService()
        self.text_chunking_service = TextChunkingService()

    async def upload_document(
        self,
        user_id: uuid.UUID,
        file: UploadFile,
    ) -> Document:
        UPLOAD_DIR.mkdir(exist_ok=True)

        original_filename = file.filename or ""
        file_extension = Path(original_filename).suffix.lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and TXT files are supported",
            )

        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size cannot exceed 10 MB",
            )

        stored_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / stored_filename
        file_path.write_bytes(file_content)

        document = await self.document_repository.create(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(file_content),
        )

        try:
            text = self.text_extraction_service.extract_text(file_path)

            if not text.strip():
                raise ValueError("No readable text found in file")

            chunks = self.text_chunking_service.split_text(text)

            document_chunks = await self.chunk_repository.create_many(
                document_id=document.id,
                chunks=chunks,
            )

            embedding_service = EmbeddingService()

            embeddings = await embedding_service.create_embeddings(
                texts=chunks,
            )

            await self.chunk_repository.add_embeddings(
                document_chunks=document_chunks,
                embeddings=embeddings,
            )

            return await self.document_repository.update_status(
                document=document,
                status="processed",
            )


        except Exception:

            await self.chunk_repository.delete_by_document(

                document_id=document.id,

            )

            await self.document_repository.update_status(

                document=document,

                status="failed",

            )

            if file_path.exists():
                file_path.unlink()

            raise

    async def list_documents(
            self,
            user_id: uuid.UUID,
            page: int,
            page_size: int,
    ) -> tuple[list[Document], int]:
        return await self.document_repository.list_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

    async def get_document(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Document | None:
        return await self.document_repository.get_by_id(
            document_id=document_id,
            user_id=user_id,
        )

    async def delete_document(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        document = await self.document_repository.get_by_id(
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            return False

        file_path = UPLOAD_DIR / document.stored_filename

        await self.chunk_repository.delete_by_document(
            document_id=document.id,
        )

        await self.document_repository.delete(document)

        if file_path.exists():
            file_path.unlink()

        return True
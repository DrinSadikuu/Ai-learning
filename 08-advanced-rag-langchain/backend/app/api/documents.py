from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import (
    DocumentUploadResponse,
    PageResponse,
)
from app.services.document_service import document_service
from app.services.vector_store_service import vector_store_service


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIRECTORY = Path("uploads")

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
) -> DocumentUploadResponse:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    original_filename = file.filename or "document.pdf"

    document_id = str(uuid4())

    stored_filename = (
        f"{document_id}_{original_filename}"
    )

    file_path = (
        UPLOAD_DIRECTORY / stored_filename
    )

    try:
        with file_path.open("wb") as destination:
            copyfileobj(
                file.file,
                destination,
            )

        documents = document_service.load_pdf(
            file_path,
        )

        chunks = document_service.split_documents(
            documents,
        )

        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
            chunk.metadata["filename"] = original_filename

        await vector_store_service.add_documents(
            chunks,
        )

        pages = [
            PageResponse(
                page_number=(
                    int(
                        document.metadata.get(
                            "page",
                            index,
                        )
                    )
                    + 1
                ),
                content=document.page_content,
                source=document.metadata.get(
                    "source"
                ),
            )
            for index, document in enumerate(
                documents
            )
        ]

        return DocumentUploadResponse(
            document_id=document_id,
            filename=original_filename,
            total_pages=len(documents),
            pages=pages,
        )

    except Exception:
        if file_path.exists():
            file_path.unlink()

        raise

    finally:
        await file.close()


@router.get("/search")
async def search_documents(
    query: str,
    document_id: str | None = None,
):
    results = await vector_store_service.search(
        query=query,
        document_id=document_id,
    )

    return [
        {
            "content": document.page_content,
            "metadata": document.metadata,
            "score": score,
        }
        for document, score in results
    ]
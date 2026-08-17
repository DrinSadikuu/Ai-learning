from pathlib import Path

from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.services.document_service import document_service
from app.services.vector_store_service import vector_store_service

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    document_id = str(uuid4())

    file_path = Path("uploads") / f"{document_id}_{file.filename}"

    content = await file.read()
    file_path.write_bytes(content)

    chunks = await document_service.load_and_split(file_path)

    for chunk in chunks:
        chunk.metadata["document_id"] = document_id
        chunk.metadata["filename"] = file.filename

    await vector_store_service.add_documents(chunks)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "chunks": len(chunks),
    }
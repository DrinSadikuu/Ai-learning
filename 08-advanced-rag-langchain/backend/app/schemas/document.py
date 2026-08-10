from pydantic import BaseModel


class PageResponse(BaseModel):
    page_number: int
    content: str
    source: str | None = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    total_pages: int
    pages: list[PageResponse]
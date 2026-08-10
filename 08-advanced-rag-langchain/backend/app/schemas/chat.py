from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    document_id: str | None = None


class SourceResponse(BaseModel):
    document_id: str | None = None
    filename: str | None = None
    page: int | None = None
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
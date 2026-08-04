import uuid

from pydantic import BaseModel, Field
from app.schemas.message import MessageResponse


class RAGRequest(BaseModel):
    question: str = Field(min_length=1)


class RAGSourceResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    content: str


class RAGResponse(BaseModel):
    answer: str
    sources: list[RAGSourceResponse]

class ConversationRAGResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: list[RAGSourceResponse]
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document_chunk import DocumentChunk
from app.db.models.message import Message
from app.services.ai_service import AIService
from app.services.search_service import SearchService


class RAGService:
    def __init__(self, db: AsyncSession):
        self.search_service = SearchService(db)
        self.ai_service = AIService()

    async def generate_answer(
        self,
        user_id: uuid.UUID,
        question: str,
        conversation_messages: list[Message] | None = None,
    ) -> tuple[str, list[DocumentChunk]]:
        chunks = await self.search_service.search(
            user_id=user_id,
            query=question,
            limit=5,
        )

        if not chunks:
            return (
                "I could not find relevant information in your documents.",
                [],
            )

        context = "\n\n".join(
            chunk.content
            for chunk in chunks
        )

        history = ""

        if conversation_messages:
            history = "\n".join(
                f"{message.role}: {message.content}"
                for message in conversation_messages[-10:]
            )

        prompt = (
            f"Previous conversation:\n{history}\n\n"
            f"Document context:\n{context}\n\n"
            f"Current question:\n{question}"
        )

        answer = await self.ai_service.generate_response_from_prompt(
            prompt=prompt,
        )

        return answer, chunks
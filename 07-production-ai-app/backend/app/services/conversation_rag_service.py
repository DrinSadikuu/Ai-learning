import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document_chunk import DocumentChunk
from app.db.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.rag_service import RAGService


class ConversationRAGService:
    def __init__(self, db: AsyncSession):
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)
        self.rag_service = RAGService(db)

    async def ask(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        question: str,
    ) -> tuple[Message, Message, list[DocumentChunk]] | None:
        conversation = await self.conversation_repository.get_by_id(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return None

        previous_messages = await self.message_repository.list_by_conversation(
            conversation_id=conversation_id,
        )

        user_message = await self.message_repository.create(
            conversation_id=conversation_id,
            role="user",
            content=question,
        )

        answer, chunks = await self.rag_service.generate_answer(
            user_id=user_id,
            question=question,
            conversation_messages=previous_messages,
        )

        assistant_message = await self.message_repository.create(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

        await self.conversation_repository.update_timestamp(
            conversation_id=conversation_id,
        )

        return user_message, assistant_message, chunks
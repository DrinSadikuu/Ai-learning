import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.ai_service import AIService


class MessageService:
    def __init__(self, db: AsyncSession):
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)
        self.ai_service = AIService()

    async def create_message(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> tuple[Message, Message] | None:
        conversation = await self.conversation_repository.get_by_id(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return None

        user_message = await self.message_repository.create(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        messages = await self.message_repository.list_by_conversation(
            conversation_id=conversation_id,
        )

        assistant_content = await self.ai_service.generate_response(
            messages=messages,
        )

        assistant_message = await self.message_repository.create(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_content,
        )

        await self.conversation_repository.update_timestamp(
            conversation_id=conversation_id,
        )

        return user_message, assistant_message

    async def list_messages(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Message] | None:
        conversation = await self.conversation_repository.get_by_id(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return None

        return await self.message_repository.list_by_conversation(
            conversation_id=conversation_id,
        )
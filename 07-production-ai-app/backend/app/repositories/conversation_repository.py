import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.models.conversation import Conversation
from sqlalchemy import func, select, update


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_by_id(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def list_by_user(
            self,
            user_id: uuid.UUID,
            page: int,
            page_size: int,
    ) -> tuple[list[Conversation], int]:
        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        total_result = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == user_id
            )
        )

        conversations = list(result.scalars().all())
        total = total_result.scalar_one()

        return conversations, total

    async def update_timestamp(
            self,
            conversation_id: uuid.UUID,
    ) -> None:
        await self.db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=func.now())
        )

        await self.db.commit()

    async def delete(
            self,
            conversation: Conversation,
    ) -> None:
        await self.db.delete(conversation)
        await self.db.commit()

    async def update_title(
            self,
            conversation: Conversation,
            title: str,
    ) -> Conversation:
        conversation.title = title

        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation
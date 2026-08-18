from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import get_settings


class CheckpointerService:
    def __init__(self) -> None:
        self.context_manager = None
        self.checkpointer = None

    async def initialize(self) -> None:
        settings = get_settings()

        database_url = settings.database_url.replace(
            "postgresql+psycopg://",
            "postgresql://",
        )

        self.context_manager = (
            AsyncPostgresSaver.from_conn_string(
                database_url
            )
        )

        self.checkpointer = (
            await self.context_manager.__aenter__()
        )

        await self.checkpointer.setup()

    async def close(self) -> None:
        if self.context_manager is not None:
            await self.context_manager.__aexit__(
                None,
                None,
                None,
            )


checkpointer_service = CheckpointerService()
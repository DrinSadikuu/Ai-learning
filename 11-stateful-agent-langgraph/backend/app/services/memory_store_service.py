from langgraph.store.postgres import AsyncPostgresStore

from app.core.config import get_settings


class MemoryStoreService:
    def __init__(self) -> None:
        self.context_manager = None
        self.store = None

    async def initialize(self) -> None:
        settings = get_settings()

        database_url = settings.database_url.replace(
            "postgresql+psycopg://",
            "postgresql://",
        )

        self.context_manager = (
            AsyncPostgresStore.from_conn_string(
                database_url
            )
        )

        self.store = (
            await self.context_manager.__aenter__()
        )

        await self.store.setup()

    async def close(self) -> None:
        if self.context_manager is not None:
            await self.context_manager.__aexit__(
                None,
                None,
                None,
            )


memory_store_service = MemoryStoreService()
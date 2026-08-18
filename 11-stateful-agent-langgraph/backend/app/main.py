from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.services.checkpointer_service import (
    checkpointer_service,
)
from app.services.graph_service import graph_service
from app.services.memory_store_service import (
    memory_store_service,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await checkpointer_service.initialize()

    await memory_store_service.initialize()

    graph_service.initialize(
        checkpointer=checkpointer_service.checkpointer,
        store=memory_store_service.store,
    )

    yield

    await memory_store_service.close()

    await checkpointer_service.close()


app = FastAPI(
    title="Stateful Agent API",
    lifespan=lifespan,
)

app.include_router(chat_router)
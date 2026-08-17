import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.services.vector_store_service import vector_store_service
from app.api.routes.documents import router as documents_router
from app.api.routes.sdk_agent import router as sdk_agent_router


if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await vector_store_service.initialize()
    yield


app = FastAPI(
    title="Project 10 - Tool-Calling Research Agent",
    lifespan=lifespan,
)

app.include_router(agent_router)
app.include_router(documents_router)
app.include_router(sdk_agent_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
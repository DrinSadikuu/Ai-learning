from fastapi import FastAPI
from pydantic import BaseModel

from app.core.tracing import setup_tracing


setup_tracing()


from app.services.llm_service import llm_service


app = FastAPI(
    title="12-ai-evaluation-observability",
)


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    return {
        "status": "ok",
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    answer = await llm_service.generate(
        question=request.question,
    )

    return {
        "question": request.question,
        "answer": answer,
    }
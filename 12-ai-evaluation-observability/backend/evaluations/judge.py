from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import get_settings


class JudgeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correctness: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    conciseness: int = Field(ge=0, le=100)
    reasoning: str


class LLMJudge:
    def __init__(self):
        settings = get_settings()

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

        self.model = settings.openai_model

    async def evaluate(
        self,
        question: str,
        answer: str,
        expected_answer: str,
    ) -> JudgeResult:
        prompt = f"""
You are evaluating an AI-generated answer.

Question:
{question}

Expected answer:
{expected_answer}

AI answer:
{answer}

Evaluate the AI answer on three dimensions.

1. Correctness:
How factually correct is the answer?
Score from 0 to 100.

2. Relevance:
How directly and completely does the answer address the question?
Score from 0 to 100.

3. Conciseness:
Is the answer focused and reasonably concise without unnecessary information?
Score from 0 to 100.

Provide a short explanation for your scores.
"""

        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "judge_result",
                    "schema": JudgeResult.model_json_schema(),
                    "strict": True,
                }
            },
        )

        return JudgeResult.model_validate_json(
            response.output_text
        )


llm_judge = LLMJudge()
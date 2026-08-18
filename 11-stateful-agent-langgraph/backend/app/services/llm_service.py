from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.tools.calculator import add_numbers


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()

        self.tools = [
            add_numbers,
        ]

        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )

        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )


llm_service = LLMService()
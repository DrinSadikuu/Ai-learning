from langchain_openai import ChatOpenAI

from app.core.config import get_settings

class LLMService:
    def __init__(self) -> None:
        settings = get_settings()

        self.model = ChatOpenAI(
            model = settings.openai_model,
            api_key = settings.openai_api_key,
            temperature=0,
        )

    async def generate_response(self, message:str)->str:
        response = await self.model.ainvoke(message)
        return str(response.content)

llm_service = LLMService()
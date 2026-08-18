from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.graphs.research_graph import create_research_graph


class GraphService:
    def __init__(self) -> None:
        self.graph = None

    def initialize(
            self,
            checkpointer,
            store,
    ) -> None:
        self.graph = create_research_graph(
            checkpointer=checkpointer,
            store=store,
        )

    async def run(
            self,
            question: str,
            thread_id: str,
            user_id: str,
    ) -> str:
        if self.graph is None:
            raise RuntimeError(
                "Graph service is not initialized"
            )

        try:
            result = await self.graph.ainvoke(
                {
                    "question": question,
                    "answer": "",
                    "valid_question": False,
                    "retry_count": 0,
                    "answer_valid": False,
                    "approved": False,
                    "messages": [
                        HumanMessage(content=question),
                    ],
                },
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "user_id": user_id,
                    }
                },
            )

            return result["answer"]

        except Exception:
            return (
                "The workflow could not complete because "
                "of a temporary system error. Please try again."
            )

    async def get_state(self, thread_id: str):
        if self.graph is None:
            raise RuntimeError(
                "Graph service is not initialized"
            )

        state = await self.graph.aget_state(
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            }
        )

        return state

    async def resume(
            self,
            thread_id: str,
            approved: bool,
    ) -> str:
        if self.graph is None:
            raise RuntimeError(
                "Graph service is not initialized"
            )

        try:
            result = await self.graph.ainvoke(
                Command(
                    resume=approved,
                ),
                config={
                    "configurable": {
                        "thread_id": thread_id,
                    }
                },
            )

            return result["answer"]

        except Exception:
            return (
                "The workflow could not resume because "
                "of a temporary system error. Please try again."
            )



graph_service = GraphService()
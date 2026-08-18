from dataclasses import dataclass
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
)
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.runtime import Runtime
from langgraph.types import RetryPolicy, interrupt

from app.services.llm_service import llm_service


class AgentState(TypedDict):
    question: str
    answer: str
    valid_question: bool
    retry_count: int
    answer_valid: bool
    approved: bool
    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]


@dataclass
class GraphContext:
    user_id: str


async def prepare_question(
    state: AgentState,
) -> dict:
    question = state["question"].strip()

    return {
        "question": question,
        "valid_question": bool(question),
    }


async def save_memory(
    state: AgentState,
    runtime: Runtime[GraphContext],
) -> dict:
    user_id = runtime.context.user_id

    namespace = (
        "users",
        user_id,
        "memories",
    )

    question = state["question"]

    if "remember" in question.lower():
        await runtime.store.aput(
            namespace,
            "profile",
            {
                "memory": question,
            },
        )

    return {}


async def generate_answer(
    state: AgentState,
) -> dict:
    response = await llm_service.llm_with_tools.ainvoke(
        state["messages"]
    )

    return {
        "answer": response.content,
        "answer_valid": False,
        "messages": [
            response,
        ],
    }


async def invalid_question(
    state: AgentState,
) -> dict:
    return {
        "answer": "Please provide a question.",
        "valid_question": False,
    }


async def check_answer(
    state: AgentState,
) -> dict:
    prompt = f"""
Question:
{state["question"]}

Answer:
{state["answer"]}

Is the answer relevant and useful for the question?

Respond only with:
YES
or
NO
"""

    response = await llm_service.llm.ainvoke(
        prompt
    )

    answer_valid = (
        response.content.strip().upper() == "YES"
    )

    return {
        "answer_valid": answer_valid,
    }


async def increment_retry(
    state: AgentState,
) -> dict:
    return {
        "retry_count": state["retry_count"] + 1,
    }


async def human_approval(
    state: AgentState,
) -> dict:
    decision = interrupt(
        {
            "question": state["question"],
            "answer": state["answer"],
            "message": "Approve this answer?",
        }
    )

    if decision:
        return {
            "approved": True,
        }

    return {
        "approved": False,
        "messages": [
            HumanMessage(
                content=(
                    "The previous answer was rejected. "
                    "Generate a different and improved answer."
                )
            )
        ],
    }


def route_question(
    state: AgentState,
) -> str:
    if state["valid_question"]:
        return "save_memory"

    return "invalid_question"


def route_answer(
    state: AgentState,
) -> str:
    if state["answer_valid"]:
        return "human_approval"

    if state["retry_count"] >= 2:
        return "human_approval"

    return "retry"

async def load_memory(
    state: AgentState,
    runtime: Runtime[GraphContext],
) -> dict:
    user_id = runtime.context.user_id

    namespace = (
        "users",
        user_id,
        "memories",
    )

    memory_item = await runtime.store.aget(
        namespace,
        "profile",
    )

    if memory_item is None:
        return {}

    memory_text = memory_item.value.get(
        "memory",
        "",
    )

    if not memory_text:
        return {}

    return {
        "messages": [
            HumanMessage(
                content=(
                    "Long-term memory about this user: "
                    f"{memory_text}"
                )
            )
        ],
    }


def route_approval(
    state: AgentState,
) -> str:
    if state["approved"]:
        return "end"

    return "retry"


graph_builder = StateGraph(
    AgentState,
    context_schema=GraphContext,
)

tool_node = ToolNode(
    llm_service.tools
)


# Nodes

graph_builder.add_node(
    "prepare_question",
    prepare_question,
)

graph_builder.add_node(
    "save_memory",
    save_memory,
)

graph_builder.add_node(
    "generate_answer",
    generate_answer,
    retry_policy=RetryPolicy(
        max_attempts=3,
    ),
)

graph_builder.add_node(
    "tools",
    tool_node,
    retry_policy=RetryPolicy(
        max_attempts=3,
    ),
)

graph_builder.add_node(
    "invalid_question",
    invalid_question,
)

graph_builder.add_node(
    "check_answer",
    check_answer,
)

graph_builder.add_node(
    "increment_retry",
    increment_retry,
)

graph_builder.add_node(
    "human_approval",
    human_approval,
)

graph_builder.add_node(
    "load_memory",
    load_memory,
)


# Start

graph_builder.set_entry_point(
    "prepare_question"
)


# Question routing

graph_builder.add_conditional_edges(
    "prepare_question",
    route_question,
    {
        "save_memory": "save_memory",
        "invalid_question": "invalid_question",
    },
)


# Memory node continues to LLM

graph_builder.add_edge(
    "save_memory",
    "load_memory",
)

graph_builder.add_edge(
    "load_memory",
    "generate_answer",
)


# Invalid question ends immediately

graph_builder.add_edge(
    "invalid_question",
    END,
)


# LLM decides whether to call tools

graph_builder.add_conditional_edges(
    "generate_answer",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "check_answer",
    },
)


# Tool result goes back to LLM

graph_builder.add_edge(
    "tools",
    "generate_answer",
)


# Verification decides retry or approval

graph_builder.add_conditional_edges(
    "check_answer",
    route_answer,
    {
        "retry": "increment_retry",
        "human_approval": "human_approval",
    },
)


# Real retry increments counter first

graph_builder.add_edge(
    "increment_retry",
    "generate_answer",
)


# Human approval decides finish or retry

graph_builder.add_conditional_edges(
    "human_approval",
    route_approval,
    {
        "end": END,
        "retry": "generate_answer",
    },
)


def create_research_graph(
    checkpointer,
    store,
):
    return graph_builder.compile(
        checkpointer=checkpointer,
        store=store,
    )
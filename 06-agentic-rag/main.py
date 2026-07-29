from agent import run_agent


MAX_HISTORY_MESSAGES = 6


def trim_conversation_history(
    conversation_history: list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Keep only the most recent conversation messages.

    Six messages represent approximately three complete
    user-assistant exchanges.
    """

    return conversation_history[
        -MAX_HISTORY_MESSAGES:
    ]


def main() -> None:
    print("Agentic RAG Assistant")
    print("Type 'exit' to stop.")
    print("Type 'clear' to clear conversation memory.\n")

    conversation_history: list[
        dict[str, str]
    ] = []

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Assistant: Goodbye.")
            break

        if question.lower() == "clear":
            conversation_history.clear()

            print(
                "Assistant: Conversation memory cleared.\n"
            )
            continue

        if not question:
            print(
                "Assistant: Please enter a question.\n"
            )
            continue

        try:
            answer = run_agent(
                question=question,
                conversation_history=conversation_history,
            )

            print(f"\nAssistant: {answer}\n")

            conversation_history.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            conversation_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            conversation_history = (
                trim_conversation_history(
                    conversation_history
                )
            )

        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
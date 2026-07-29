from agent import run_agent


def main() -> None:
    print("Agentic RAG Assistant")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Assistant: Goodbye.")
            break

        if not question:
            print("Assistant: Please enter a question.\n")
            continue

        try:
            answer = run_agent(question)

            print(f"\nAssistant: {answer}\n")

        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
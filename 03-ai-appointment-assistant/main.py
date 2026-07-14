from assistant import ask_ai
from database import initialize_database


def main() -> None:
    initialize_database()

    print("AI Appointment Assistant")
    print("Type 'exit' to stop.\n")

    previous_response_id = None

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() == "exit":
            print("Assistant: Goodbye.")
            break

        if not user_message:
            continue

        try:
            answer, previous_response_id = ask_ai(
                message=user_message,
                previous_response_id=previous_response_id,
            )

            print(f"Assistant: {answer}\n")

        except Exception as error:
            print(f"Error: {error}\n")


if __name__ == "__main__":
    main()
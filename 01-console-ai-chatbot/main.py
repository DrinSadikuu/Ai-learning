from chatbot import stream_message

print("AI Chatbot")
print("Type 'exit' to stop.\n")

while True:
    user_message = input("You: ").strip()

    if user_message.lower() == "exit":
        print("Chatbot: Goodbye!")
        break

    if not user_message:
        print("Chatbot: Please enter a message.")
        continue

    try:
        print("Chatbot: ", end="", flush=True)

        for text_piece in stream_message(user_message):
            print(text_piece, end="", flush=True)

        print("\n")

    except Exception as error:
        print("\nSomething went wrong:", error)
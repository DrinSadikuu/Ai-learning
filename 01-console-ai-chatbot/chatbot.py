from config import openai
from prompts import SYSTEM_PROMPT

conversation = []


def stream_message(user_message: str):
    conversation.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    full_response = ""

    try:
        stream = openai.responses.create(
            model="gpt-5-nano",
            instructions=SYSTEM_PROMPT,
            input=conversation,
            stream=True,
        )

        for event in stream:
            if event.type == "response.output_text.delta":
                text_piece = event.delta
                full_response += text_piece
                yield text_piece

        conversation.append(
            {
                "role": "assistant",
                "content": full_response,
            }
        )

    except Exception:
        conversation.pop()
        raise
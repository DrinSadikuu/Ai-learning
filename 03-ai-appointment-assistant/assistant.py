import json

from dotenv import load_dotenv
from openai import OpenAI

from appointment_service import (
    cancel_appointment,
    create_appointment,
    get_available_slots,
    list_appointments,
    update_appointment
)
from tools import TOOLS
from datetime import date

TOOL_FUNCTIONS = {
    "get_available_slots": get_available_slots,
    "create_appointment": create_appointment,
    "cancel_appointment": cancel_appointment,
    "list_appointments": list_appointments,
    "update_appointment": update_appointment,
}


load_dotenv()

today = date.today().isoformat()

client = OpenAI()

def ask_ai(
    message: str,
    previous_response_id: str | None = None,
) -> tuple[str, str]:

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            f"You are an appointment assistant. "
            f"Today's date is {today}. "
            "Convert relative dates such as tomorrow, next Friday, or Monday "
            "into YYYY-MM-DD format before calling a tool. "
            "Use the available tools to view, create, cancel, or reschedule appointments. "
            "When the user provides a name, date, and time, call create_appointment immediately. "
            "Do not ask for purpose, notes, contact information, or confirmation because they are not required. "
            "Never claim an action succeeded unless the corresponding tool succeeds."
        ),
        input=message,
        tools=TOOLS,
        previous_response_id=previous_response_id,
    )

    for item in response.output:
        if item.type != "function_call":
            continue

        arguments = json.loads(item.arguments)

        tool_function = TOOL_FUNCTIONS.get(item.name)

        if tool_function is None:
            result = {
                "success": False,
                "error": f"Unknown tool: {item.name}",
            }

        else:
            try:
                result = tool_function(**arguments)

            except ValueError as error:
                result = {
                    "success": False,
                    "error": str(error),
                }

            except Exception:
                result = {
                    "success": False,
                    "error": "An unexpected error occurred while executing the tool.",
                }

        final_response = client.responses.create(
            model="gpt-4.1-mini",
            previous_response_id=response.id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            ],
        )

        return final_response.output_text, final_response.id

    return response.output_text, response.id
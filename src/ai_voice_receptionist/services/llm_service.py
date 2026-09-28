import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from ai_voice_receptionist.services.appointment_service import check_availability

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


SYSTEM_INSTRUCTION = """
You are an AI receptionist for a small business.

Your responsibilities:
- Answer questions about the business.
- Help customers with appointment-related requests.
- Be polite, helpful, and concise.
- Ask for missing information when necessary.
- Never claim that an appointment has been booked unless the booking system confirms it.
- Never invent business information or appointment availability.
"""

check_availability_tool = {
    "name": "check_availability",
    "description": "Check whether a specific appointment date and time is available.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Appointment date in YYYY-MM-DD format."
            },
            "time": {
                "type": "string",
                "description": "Appointment time in HH:MM format."
            }
        },
        "required": ["date", "time"]
    }
}

tools = types.Tool(function_declarations=[check_availability_tool])
def generate_response(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "tools": [tools],
            
        },
    )
    function_call = response.candidates[0].content.parts[0].function_call

    if function_call:

        if function_call.name == "check_availability":
            date = function_call.args["date"]
            time = function_call.args["time"]

            result = check_availability(date, time)

            function_response_part = types.Part.from_function_response(
                name=function_call.name,
                response={
                    "available": result
                },
            )

            final_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=message)
                        ],
                    ),
                    response.candidates[0].content,
                    types.Content(
                        role="tool",
                        parts=[function_response_part],
                    ),
                ],
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                },
            )

            return final_response.text

    return response.text
    




import os
from datetime import date

from dotenv import load_dotenv
from google import genai
from google.genai import types

from ai_voice_receptionist.services.appointment_service import (check_availability , book_appointment ,  validate_appointment_date)

load_dotenv()
today = date.today().isoformat()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


SYSTEM_INSTRUCTION = f"""
Today's date is {today}.
You are an AI receptionist for a small business.

Your responsibilities:
- Answer questions about the business.
- Help customers with appointment-related requests.
- Be polite, helpful, and concise.
- Ask for missing information when necessary.
- Never claim that an appointment has been booked unless the booking system confirms it.
- Never invent business information or appointment availability.
- Always check appointment availability before asking for the customer's name.
- If the requested appointment date/time is in the past, tell the customer that it has already passed and do not ask for their name.
- If a requested slot is unavailable, explain that it is unavailable and do not proceed with booking.
- Only ask for the customer's name after an available appointment slot has been confirmed.
- If the requested date is a closed business day, inform the customer that the business is closed on that day and ask them to choose another date.
"""

check_availability_tool = {
    "name": "check_availability",
    "description": """Check whether a specific appointment date and time is available.The result can be:- available: the slot can be booked.- past_date: the requested date and time has already passed.- not_found: the requested date or time is not in the appointment schedule.- already_booked: the slot exists but is already booked.""",
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
book_appointment_tool = {
    "name": "book_appointment",
    "description": "Book an available appointment for a customer.",
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
            },
            "customer_name": {
                "type": "string",
                "description": "Name of the customer booking the appointment."
            }
        },
        "required": ["date", "time", "customer_name"]
    }
}

validate_appointment_date_tool = {
    "name": "validate_appointment_date",
    "description": """
    Validate an appointment date before asking for or checking an appointment time.

    Use this when the customer provides a date but has not provided a time yet.

    The result can be:
    - past_date: the requested date has already passed.
    - today: the requested date is today.
    - future_date: the requested date is in the future.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Appointment date in YYYY-MM-DD format."
            }
        },
        "required": ["date"]
    }
}
tools = types.Tool(function_declarations=[check_availability_tool , book_appointment_tool , validate_appointment_date_tool])

chats = {}

def reset_session(session_id: str) -> bool:
    if session_id in chats:
        del chats[session_id]
        return True

    return False

def generate_response(message: str , session_id:str) -> str:
    if session_id not in chats:
        chats[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "tools": [tools],
            },
        )

    chat = chats[session_id]
    response = chat.send_message(message)
    function_call = response.candidates[0].content.parts[0].function_call

    if function_call:


        if function_call.name == "validate_appointment_date":
            date = function_call.args["date"]

            result = validate_appointment_date(date)

        elif function_call.name == "check_availability":
            date = function_call.args["date"]
            time = function_call.args["time"]

            result = check_availability(date, time)


        elif function_call.name == "book_appointment":
            date = function_call.args["date"]
            time = function_call.args["time"]
            customer_name = function_call.args["customer_name"]

            result = book_appointment(
                date,
                time,
                customer_name
            )

        else:
            return "I couldn't process that request."
        
        function_response_part = types.Part.from_function_response(
                name=function_call.name,
                response={
                    "result": result
                },
            )

        final_response = chat.send_message(
                function_response_part,
            )

        return final_response.text

    return response.text
    




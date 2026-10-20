import os
from datetime import date
from urllib import response

from dotenv import load_dotenv
from google import genai
from google.genai import types

from ai_voice_receptionist.services.appointment_service import (check_availability , book_appointment ,  validate_appointment_date ,  cancel_appointment , get_appointment_by_id , reschedule_appointment)

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
- When an appointment is successfully booked, tell the customer that the booking was successful and provide the appointment ID.
- Tell the customer to keep the appointment ID for future cancellation or rescheduling.
- Never provide an appointment ID unless the booking system has returned one.
- When a customer wants to cancel an appointment, ask for the appointment ID if they have not provided it.
- Do not claim that an appointment was cancelled unless the cancellation system confirms it.
- After a successful cancellation, clearly confirm that the appointment has been cancelled.
- If the appointment ID is invalid or the appointment is already cancelled, explain that the appointment could not be cancelled.
- When a customer wants to cancel an appointment and provides an appointment ID, first retrieve the appointment details using the appointment lookup tool.
- Before cancelling, tell the customer the appointment ID, customer name, date, and time and ask them to confirm that it is the correct appointment.
- Do not call the cancellation tool until the customer explicitly confirms the appointment.
- If the customer does not confirm, do not cancel the appointment.
- If no appointment is found for the provided ID, tell the customer that the appointment could not be found.
- When a customer wants to reschedule an appointment, ask for the appointment ID if they have not provided it.
- When the customer provides an appointment ID for rescheduling, first retrieve the appointment using the appointment lookup tool.
- Show the customer name, current appointment date, and current appointment time and ask the customer to confirm that it is the correct appointment.
- Do not reschedule an appointment until the customer confirms the appointment details.
- After the customer confirms the existing appointment, ask for the new desired date and time.
- Always check availability of the new date and time before rescheduling.
- Never reschedule an appointment to an unavailable or invalid slot.
- Do not call the reschedule tool until the new slot has been confirmed as available.
- After a successful rescheduling, tell the customer the new appointment date and time and provide the appointment ID.
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


cancel_appointment_tool = {
    "name": "cancel_appointment",
    "description": """
    Cancel an existing booked appointment.

    Use this when the customer wants to cancel an appointment.
    The appointment must be identified by its appointment ID.

    The result is:
    - True: appointment was successfully cancelled.
    - False: appointment was not found or was already cancelled.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {
                "type": "integer",
                "description": "The ID of the appointment to cancel."
            }
        },
        "required": ["appointment_id"]
    }
}

get_appointment_tool = {
    "name": "get_appointment_by_id",
    "description": """
    Find an appointment using its appointment ID.

    Use this when a customer wants to cancel or reschedule an appointment
    and provides an appointment ID.

    Return the appointment details so they can be confirmed with the customer
    before any cancellation or rescheduling is performed.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {
                "type": "integer",
                "description": "The ID of the appointment to look up."
            }
        },
        "required": ["appointment_id"]
    }
}


reschedule_appointment_tool = {
    "name": "reschedule_appointment",
    "description": """
    Reschedule an existing booked appointment to a new date and time.

    Use this only after:
    1. The appointment has been identified using its appointment ID.
    2. The customer has confirmed that the appointment details are correct.
    3. The new date and time have been checked for availability.

    The result is:
    - True: appointment was successfully rescheduled.
    - False: the new slot is unavailable or the appointment could not be updated.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "appointment_id": {
                "type": "integer",
                "description": "The ID of the existing appointment."
            },
            "new_date": {
                "type": "string",
                "description": "The new appointment date in YYYY-MM-DD format."
            },
            "new_time": {
                "type": "string",
                "description": "The new appointment time in HH:MM format."
            }
        },
        "required": ["appointment_id", "new_date", "new_time"]
    }
}
tools = types.Tool(function_declarations=[check_availability_tool , book_appointment_tool , validate_appointment_date_tool ,cancel_appointment_tool , get_appointment_tool , reschedule_appointment_tool])

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

    function_call = None

    for part in response.candidates[0].content.parts:
        if part.function_call:
            function_call = part.function_call
            break

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

        elif function_call.name == "get_appointment_by_id":
            appointment_id = function_call.args["appointment_id"]

            result = get_appointment_by_id(appointment_id)

        elif function_call.name == "cancel_appointment":
            appointment_id = function_call.args["appointment_id"]

            result = cancel_appointment(appointment_id)

        elif function_call.name == "reschedule_appointment":
            appointment_id = function_call.args["appointment_id"]
            new_date = function_call.args["new_date"]
            new_time = function_call.args["new_time"]

            result = reschedule_appointment(
            appointment_id,
            new_date,
            new_time
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
    




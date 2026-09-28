import os

from dotenv import load_dotenv
from google import genai

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
def generate_response(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            
        },
    )

    return response.text
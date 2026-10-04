from fastapi import FastAPI
from pydantic import BaseModel

from ai_voice_receptionist.services.llm_service import (generate_response , reset_session )
from ai_voice_receptionist.services.appointment_service import (get_appointments , cancel_appointment)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


class MessageRequest(BaseModel):
    session_id:str
    message: str


@app.post("/message")
def receive_message(request: MessageRequest):
    response = generate_response(
    request.message,
    request.session_id
    )

    return {
        "session_id": request.session_id,
        "response": response
    }
@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    deleted = reset_session(session_id)

    if deleted:
        return {
            "message": "Conversation session reset successfully."
        }

    return {
        "message": "No active session found."
    }

@app.get("/appointments")
def list_appointments(appointment_date: str = None , status:str =None):
    return {
        "appointments": get_appointments(appointment_date, status)
    }
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):
    cancelled = cancel_appointment(appointment_id)

    if cancelled:
        return {
            "message": "Appointment cancelled successfully."
        }

    return {
        "message": "Appointment not found or already cancelled."
    }
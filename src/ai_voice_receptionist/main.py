import logging
from fastapi import FastAPI , HTTPException
from pydantic import BaseModel

from ai_voice_receptionist.services.llm_service import (generate_response , reset_session )
from ai_voice_receptionist.services.appointment_service import (get_appointments , cancel_appointment)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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
    logger.info(
        "Received message from session: %s",
        request.session_id
    )

    try:
        response = generate_response(
            request.message,
            request.session_id
        )

        if not response:
            raise HTTPException(
                status_code=502,
                detail="The AI assistant returned an empty response."
            )

        return {
            "session_id": request.session_id,
            "response": response
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Error generating response for session: %s",
            request.session_id
        )

        raise HTTPException(
            status_code=500,
            detail="The receptionist service encountered an unexpected error. Please try again."
        )
@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    try:
        deleted = reset_session(session_id)

        if deleted:
            logger.info(
                "Session %s reset successfully",
                session_id
            )

            return {
                "message": "Conversation session reset successfully."
            }

        return {
            "message": "No active session found."
        }

    except Exception:
        logger.exception(
            "Error resetting session: %s",
            session_id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to reset conversation session."
        )
    
@app.get("/appointments")
def list_appointments(
    appointment_date: str = None,
    status: str = None
):
    try:
        appointments = get_appointments(
            appointment_date,
            status
        )

        return {"appointments": appointments}

    except Exception:
        logger.exception("Error retrieving appointments")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve appointments. Please try again."
        )
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):
    try:
        cancelled = cancel_appointment(appointment_id)

        if cancelled:
            logger.info(
                "Appointment %s cancelled successfully",
                appointment_id
            )

            return {
                "message": "Appointment cancelled successfully."
            }

        raise HTTPException(
            status_code=404,
            detail="Appointment not found or already cancelled."
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Error cancelling appointment: %s",
            appointment_id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to cancel appointment. Please try again."
        )
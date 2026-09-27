from fastapi import FastAPI
from pydantic import BaseModel

from ai_voice_receptionist.services.llm_service import generate_response


app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}


class MessageRequest(BaseModel):
    message: str


@app.post("/message")
def receive_message(request: MessageRequest):
    response = generate_response(request.message)
    return {
        "response": response
    }
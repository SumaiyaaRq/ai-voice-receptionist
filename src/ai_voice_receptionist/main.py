from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}


class MessageRequest(BaseModel):
    message: str


@app.post("/message")
def receive_message(request: MessageRequest):
    return {
        "received": request.message
    }
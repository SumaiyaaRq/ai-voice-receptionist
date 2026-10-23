import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = Path(__file__).resolve().parents[3]

CREDENTIALS_FILE = BASE_DIR / "credentials" / "credentials.json"
TOKEN_FILE = BASE_DIR / "credentials" / "token.json"


def get_calendar_service():
    """Authenticate and return a Google Calendar API service."""

    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )
            credentials = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(credentials.to_json())

    return build(
        "calendar",
        "v3",
        credentials=credentials
    )

def create_calendar_event(
    customer_name: str,
    appointment_date: str,
    appointment_time: str
):
    """Create an appointment event in Google Calendar."""

    service = get_calendar_service()

    start_datetime = datetime.strptime(
        f"{appointment_date} {appointment_time}",
        "%Y-%m-%d %H:%M"
    )

    end_datetime = start_datetime + timedelta(minutes=60)

    event = {
        "summary": f"Appointment - {customer_name}",
        "description": f"Appointment for {customer_name}",
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    created_event = service.events().insert(
        calendarId=os.getenv("GOOGLE_CALENDAR_ID"),
        body=event
    ).execute()

    return {
        "event_id": created_event["id"],
        "event_link": created_event.get("htmlLink"),
    }

def delete_calendar_event(event_id: str):
    """Delete an appointment event from Google Calendar."""

    service = get_calendar_service()

    service.events().delete(
        calendarId=os.getenv("GOOGLE_CALENDAR_ID"),
        eventId=event_id
    ).execute()

    return True

def update_calendar_event(
    event_id: str,
    customer_name: str,
    appointment_date: str,
    appointment_time: str
):
    """Update an existing appointment event in Google Calendar."""

    service = get_calendar_service()

    start_datetime = datetime.strptime(
        f"{appointment_date} {appointment_time}",
        "%Y-%m-%d %H:%M"
    )

    end_datetime = start_datetime + timedelta(minutes=60)

    event = {
        "summary": f"Appointment - {customer_name}",
        "description": f"Appointment for {customer_name}",
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    updated_event = service.events().update(
        calendarId=os.getenv("GOOGLE_CALENDAR_ID"),
        eventId=event_id,
        body=event
    ).execute()

    return {
        "event_id": updated_event["id"],
        "event_link": updated_event.get("htmlLink"),
    }
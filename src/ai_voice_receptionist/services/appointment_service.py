from datetime import date, datetime, time

MOCK_APPOINTMENTS = {
    "2026-09-29": {
        "10:00": True,
        "11:00": False,
        "15:00": True,
        "16:00": False,
    },
    "2026-10-02": {
        "15:00": True,
        "16:00": False,
    }
}

def validate_date(date: str) -> str:
    """Validate whether an appointment date is in the past, today, or future."""

    appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
    today = datetime.now().date()

    if appointment_date < today:
        return "past_date"

    if appointment_date == today:
        return "today"

    return "future_date"

def validate_appointment_date(date: str) -> str:
    """Validate an appointment date before checking a specific time."""

    return validate_date(date)

def validate_datetime(date: str, time: str) -> str:
    """Validate whether an appointment date and time can be booked."""

    appointment_datetime = datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %H:%M"
    )

    if appointment_datetime < datetime.now():
        return "past_datetime"

    return "valid"

def check_availability(date: str, time: str) -> bool:
    """Check whether a specific appointment slot is available."""

    date_status = validate_date(date)

    if date_status == "past_date":
        return "past_date"
    
    datetime_status = validate_datetime(date, time)
    if datetime_status == "past_datetime":
        return "past_datetime"

    if date not in MOCK_APPOINTMENTS:
        return "not_found"

    if time not in MOCK_APPOINTMENTS[date]:
        return "not_found"

    if not MOCK_APPOINTMENTS[date][time]:
        return "already_booked"

    return "available"

def book_appointment(date:str, time:str , customer_name:str)-> bool:
    """ Book an available appointment slot for a customer. """
    status = check_availability(date, time)

    if status != "available":
        return False

    MOCK_APPOINTMENTS[date][time] = False

    print(
        f"Appointment booked for {customer_name} "
        f"on {date} at {time}"
    )

    return True
MOCK_APPOINTMENTS = {
    "2026-09-29": {
        "10:00": True,
        "11:00": False,
        "15:00": True,
        "16:00": False,
    }
}


def check_availability(date: str, time: str) -> bool:
    """Check whether a specific appointment slot is available."""

    return MOCK_APPOINTMENTS.get(date, {}).get(time, False)

def book_appointment(date:str, time:str , customer_name:str)-> bool:
    """ Book an available appointment slot for a customer. """
    if not check_availability(date, time):
        return False  # Slot is not available
    MOCK_APPOINTMENTS[date][time] = False  # Mark the slot as booked

    print(
        f"Appointment booked for {customer_name} "
        f"on {date} at {time}"
    )
    return True
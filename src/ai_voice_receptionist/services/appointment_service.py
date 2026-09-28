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
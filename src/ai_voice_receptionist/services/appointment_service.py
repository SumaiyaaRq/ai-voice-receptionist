import sqlite3
from pathlib import Path
from datetime import date, datetime, time
# Store the database in the project root.
DB_PATH = Path(__file__).resolve().parents[3] / "appointments.db"

# Temporary business schedule.
# True = slot offered; False = unavailable from the initial schedule
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

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'booked',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        indexes = connection.execute(
            "PRAGMA index_list(appointments)"
        ).fetchall()

        has_old_constraint = any(
            index[2] and index[3] == "u"
            for index in indexes
        )

        if has_old_constraint:
            connection.execute(
                "ALTER TABLE appointments RENAME TO appointments_old"
            )

            connection.execute("""
                CREATE TABLE appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'booked',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                INSERT INTO appointments (
                    id,
                    customer_name,
                    appointment_date,
                    appointment_time,
                    status,
                    created_at
                )
                SELECT
                    id,
                    customer_name,
                    appointment_date,
                    appointment_time,
                    status,
                    created_at
                FROM appointments_old
            """)

            connection.execute("DROP TABLE appointments_old")

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_unique_active_appointment_slot
            ON appointments (appointment_date, appointment_time)
            WHERE status = 'booked'
        """)
initialize_database()

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

   
        
    with get_connection() as connection:
        booking = connection.execute(
                """
                SELECT id FROM appointments
                WHERE appointment_date = ?
                AND appointment_time = ?
                AND status = 'booked'
                """,
                (date, time)
            ).fetchone()

    if booking:
        return "already_booked"

    return "available"

def book_appointment(date:str, time:str , customer_name:str)-> bool:
    """ Save an appointment in SQLite if the slot is available. """
    status = check_availability(date, time)

    if status != "available":
        return False

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO appointments (
                    customer_name,
                    appointment_date,
                    appointment_time
                )
                VALUES (?, ?, ?)
                """,
                (customer_name, date, time)
            )

    # MOCK_APPOINTMENTS[date][time] = False

        print(
        f"Appointment booked for {customer_name} "
        f"on {date} at {time}"
        )

        return True

    except sqlite3.IntegrityError:
    # Prevent two bookings for the same slot.
        return False


def get_appointments():
    """Retrieve all appointment records from SQLite."""

    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        records = connection.execute(
            """
            SELECT
                id,
                customer_name,
                appointment_date,
                appointment_time,
                status,
                created_at
            FROM appointments
            ORDER BY appointment_date, appointment_time
            """
        ).fetchall()

    return [dict(record) for record in records]

def cancel_appointment(appointment_id: int) -> bool:
    """Cancel an existing appointment without deleting its record."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE appointments
            SET status = 'cancelled'
            WHERE id = ?
            AND status = 'booked'
            """,
            (appointment_id,)
        )

        return cursor.rowcount > 0
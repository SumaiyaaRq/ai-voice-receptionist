from multiprocessing.dummy import connection
import sqlite3
from pathlib import Path
from datetime import  datetime, timedelta
from ai_voice_receptionist.services.calendar_service import (create_calendar_event, delete_calendar_event,update_calendar_event,)
# Store the database in the project root.
DB_PATH = Path(__file__).resolve().parents[3] / "appointments.db"

BUSINESS_OPENING_TIME = "09:00"
BUSINESS_CLOSING_TIME = "17:00"

BUSINESS_DAYS = [0, 1, 2, 3, 4]

APPOINTMENT_DURATION_MINUTES = 60

def generate_time_slots():
    """Generate appointment slots based on business hours."""

    opening = datetime.strptime(
        BUSINESS_OPENING_TIME, "%H:%M"
    )

    closing = datetime.strptime(
        BUSINESS_CLOSING_TIME, "%H:%M"
    )

    slots = []
    current = opening

    while (
        current + timedelta(minutes=APPOINTMENT_DURATION_MINUTES)
        <= closing
    ):
        slots.append(current.strftime("%H:%M"))

        current += timedelta(
            minutes=APPOINTMENT_DURATION_MINUTES
        )

    return slots

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
                calendar_event_id TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = connection.execute(
        "PRAGMA table_info(appointments)"
        ).fetchall()

        column_names = [column[1] for column in columns]

        if "calendar_event_id" not in column_names:
            connection.execute(
            "ALTER TABLE appointments ADD COLUMN calendar_event_id TEXT"
        )

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
                    calendar_event_id TEXT,
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
    """Check availability using business hours and SQLite."""

    date_status = validate_date(date)

    if date_status == "past_date":
        return "past_date"

    appointment_date = datetime.strptime(
    date, "%Y-%m-%d"
    ).date()

    if appointment_date.weekday() not in BUSINESS_DAYS:
        return "closed_day"
    
    datetime_status = validate_datetime(date, time)
    if datetime_status == "past_datetime":
        return "past_datetime"


    if time not in generate_time_slots():
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

def book_appointment(
    date: str,
    time: str,
    customer_name: str
) -> bool:
    """Save an appointment in SQLite and Google Calendar."""

    status = check_availability(date, time)

    if status != "available":
        return False

    try:
        calendar_event = create_calendar_event(
            customer_name,
            date,
            time
        )

        calendar_event_id = calendar_event["event_id"]

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO appointments (
                    customer_name,
                    appointment_date,
                    appointment_time,
                    status,
                    calendar_event_id
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    customer_name,
                    date,
                    time,
                    "booked",
                    calendar_event_id
                )
            )

        print(
            f"Appointment booked for {customer_name} "
            f"on {date} at {time}"
        )

        return True

    except Exception as error:
        print(f"Booking error: {error}")
        return False
            
def cancel_appointment(appointment_id: int) -> bool:
    """Cancel an appointment in Google Calendar and SQLite."""

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return False

    if appointment["status"] != "booked":
        return False

    calendar_event_id = appointment.get("calendar_event_id")

    try:
        if calendar_event_id:
            delete_calendar_event(calendar_event_id)
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
    except Exception as error:
        print(f"Cancellation error: {error}")
        return False

def get_appointment_by_id(appointment_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, customer_name, appointment_date, appointment_time, status,calendar_event_id
        FROM appointments
        WHERE id = ?
        """,
        (appointment_id,)
    )

    appointment = cursor.fetchone()

    conn.close()

    if not appointment:
        return None

    return {
        "id": appointment[0],
        "customer_name": appointment[1],
        "appointment_date": appointment[2],
        "appointment_time": appointment[3],
        "status": appointment[4],
        "calendar_event_id": appointment[5],
    }

def get_appointments(
    appointment_date: str = None,
    status: str = None
):
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        query = """
            SELECT
                id,
                customer_name,
                appointment_date,
                appointment_time,
                status,
                calendar_event_id,
                created_at
            FROM appointments
            WHERE 1=1
        """

        parameters = []

        if appointment_date:
            query += " AND appointment_date = ?"
            parameters.append(appointment_date)

        if status:
            query += " AND status = ?"
            parameters.append(status)

        query += " ORDER BY appointment_date, appointment_time"

        records = connection.execute(
            query,
            parameters
        ).fetchall()

    return [dict(record) for record in records]


def reschedule_appointment(
    appointment_id: int,
    new_date: str,
    new_time: str
) -> bool:
    """Reschedule an existing appointment in Google Calendar and SQLite."""

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return False

    if appointment["status"] != "booked":
        return False

    availability = check_availability(new_date, new_time)

    if availability != "available":
        return False

    calendar_event_id = appointment.get("calendar_event_id")

    try:
        if calendar_event_id:
            update_calendar_event(
                calendar_event_id,
                appointment["customer_name"],
                new_date,
                new_time
            )

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE appointments
                SET appointment_date = ?,
                    appointment_time = ?
                WHERE id = ?
                AND status = 'booked'
                """,
                (
                    new_date,
                    new_time,
                    appointment_id
                )
            )

            return cursor.rowcount > 0

    except Exception as error:
        print(f"Rescheduling error: {error}")
        return False
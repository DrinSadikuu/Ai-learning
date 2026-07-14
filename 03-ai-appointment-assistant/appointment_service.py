from datetime import datetime
from typing import Any
from uuid import uuid4

from database import get_connection


AVAILABLE_TIMES = [
    "09:00",
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
]


def load_appointments() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, date, time, status
            FROM appointments
            ORDER BY date, time
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_available_slots(date: str) -> list[str]:
    datetime.strptime(date, "%Y-%m-%d")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT time
            FROM appointments
            WHERE date = ?
              AND status = 'booked'
            """,
            (date,),
        ).fetchall()

    booked_times = {
        row["time"]
        for row in rows
    }

    return [
        time
        for time in AVAILABLE_TIMES
        if time not in booked_times
    ]


def create_appointment(
    name: str,
    date: str,
    time: str,
) -> dict[str, Any]:
    datetime.strptime(date, "%Y-%m-%d")
    datetime.strptime(time, "%H:%M")

    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("The name cannot be empty.")

    if time not in AVAILABLE_TIMES:
        raise ValueError(
            "The selected time is not a valid appointment slot."
        )

    available_slots = get_available_slots(date)

    if time not in available_slots:
        raise ValueError(
            "The selected appointment slot is already booked."
        )

    appointment = {
        "id": str(uuid4()),
        "name": cleaned_name,
        "date": date,
        "time": time,
        "status": "booked",
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO appointments (
                id,
                name,
                date,
                time,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                appointment["id"],
                appointment["name"],
                appointment["date"],
                appointment["time"],
                appointment["status"],
            ),
        )

    return appointment


def cancel_appointment(
    appointment_id: str,
) -> dict[str, Any]:
    with get_connection() as connection:
        appointment = connection.execute(
            """
            SELECT id, name, date, time, status
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,),
        ).fetchone()

        if appointment is None:
            raise ValueError("Appointment not found.")

        if appointment["status"] == "cancelled":
            raise ValueError(
                "The appointment is already cancelled."
            )

        connection.execute(
            """
            UPDATE appointments
            SET status = 'cancelled'
            WHERE id = ?
            """,
            (appointment_id,),
        )

        updated_appointment = connection.execute(
            """
            SELECT id, name, date, time, status
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,),
        ).fetchone()

    return dict(updated_appointment)


def update_appointment(
    appointment_id: str,
    new_date: str,
    new_time: str,
) -> dict[str, Any]:
    datetime.strptime(new_date, "%Y-%m-%d")
    datetime.strptime(new_time, "%H:%M")

    if new_time not in AVAILABLE_TIMES:
        raise ValueError(
            "The selected time is not a valid appointment slot."
        )

    with get_connection() as connection:
        appointment = connection.execute(
            """
            SELECT id, name, date, time, status
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,),
        ).fetchone()

        if appointment is None:
            raise ValueError("Appointment not found.")

        if appointment["status"] == "cancelled":
            raise ValueError(
                "A cancelled appointment cannot be updated."
            )

        conflicting_appointment = connection.execute(
            """
            SELECT id
            FROM appointments
            WHERE date = ?
              AND time = ?
              AND status = 'booked'
              AND id != ?
            """,
            (
                new_date,
                new_time,
                appointment_id,
            ),
        ).fetchone()

        if conflicting_appointment is not None:
            raise ValueError(
                "The selected appointment slot is already booked."
            )

        connection.execute(
            """
            UPDATE appointments
            SET date = ?,
                time = ?
            WHERE id = ?
            """,
            (
                new_date,
                new_time,
                appointment_id,
            ),
        )

        updated_appointment = connection.execute(
            """
            SELECT id, name, date, time, status
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,),
        ).fetchone()

    return dict(updated_appointment)


def list_appointments() -> list[dict[str, Any]]:
    return load_appointments()
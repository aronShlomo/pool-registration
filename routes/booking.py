from flask import Blueprint, request, jsonify, render_template
from datetime import datetime

from database import get_db_connection

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/booking")
def booking_page():

    return render_template("booking.html")


@booking_bp.route("/check-availability", methods=["POST"])
def check_availability():

    data = request.json

    date = data.get("date")
    time = data.get("time")


    if not date or not time:
        return jsonify({
            "available": False,
            "message": "Date and time are required"
        }), 400


    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE lesson_date = ?
        AND lesson_time = ?
        AND payment_status = 'paid'
        """,
        (
            data["date"],
            data["time"]
        )
    )

    booking = cursor.fetchone()


    conn.close()


    if booking:

        return jsonify({
            "available": False,
            "message": "This time is already booked"
        })


    return jsonify({
        "available": True,
        "message": "This time is available"
    })
    
from flask import jsonify
from database import get_db_connection


@booking_bp.route("/booked-slots", methods=["GET"])
def booked_slots():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT lesson_date, lesson_time
        FROM bookings
        WHERE status IN ('pending', 'confirmed')
    """)

    rows = cursor.fetchall()
    conn.close()

    slots = []

    for row in rows:
        slots.append({
            "date": row["lesson_date"],
            "time": row["lesson_time"]
        })

    return jsonify(slots)


@booking_bp.route("/bookings", methods=["GET"])
def bookings():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            lesson_date,
            lesson_time,
            lesson_type,
            name
        FROM bookings
        WHERE status = 'confirmed'
    """)

    rows = cursor.fetchall()
    conn.close()

    events = []

    for row in rows:

        events.append({
            "title": f'{row["lesson_type"]} - {row["name"]}',
            "start": f'{row["lesson_date"]}T{row["lesson_time"]}'
        })

    return jsonify(events)    



@booking_bp.route("/create-booking", methods=["POST"])
def create_booking():

    data = request.json


    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    lesson_type = data.get("lesson_type")
    package = data.get("package")

    date = data.get("date")
    time = data.get("time")


    if not all([
        name,
        email,
        lesson_type,
        package,
        date,
        time
    ]):
        return jsonify({
            "error": "Missing information"
        }), 400



    conn = get_db_connection()

    cursor = conn.cursor()


    # Check if already booked
    cursor.execute(
        """
        SELECT id
        FROM bookings
        WHERE lesson_date = ?
        AND lesson_time = ?
        AND status != 'cancelled'
        """,
        (date, time)
    )


    existing = cursor.fetchone()


    if existing:

        conn.close()

        return jsonify({
            "error": "This time is already booked"
        }), 409



    cursor.execute(
        """
        INSERT INTO bookings
        (
        name,
        email,
        phone,
        lesson_type,
        package,
        lesson_date,
        lesson_time,
        status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            name,
            email,
            phone,
            lesson_type,
            package,
            date,
            time,
            "pending"
        )
    )


    conn.commit()

    booking_id = cursor.lastrowid

    conn.close()


    return jsonify({

        "success": True,

        "booking_id": booking_id,

        "message": "Booking created. Continue to payment."

    })
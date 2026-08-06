from flask import Blueprint, request, jsonify
from database import get_db_connection


booking_bp = Blueprint(
    "booking",
    __name__
)



# =====================================
# CREATE BOOKING
# =====================================

@booking_bp.route(
    "/create-booking",
    methods=["POST"]
)
def create_booking():

    try:

        data = request.json

        required = [
            "name",
            "email",
            "phone",
            "lesson_type",
            "package",
            "date",
            "time"
        ]


        for field in required:

            if not data.get(field):

                return jsonify({
                    "error": f"Missing {field}"
                }),400



        conn = get_db_connection()

        cursor = conn.cursor()



        # Prevent duplicate bookings

        cursor.execute(
    """
    SELECT *
    FROM bookings
    WHERE lesson_date = ?
    AND lesson_time = ?
    AND status = 'confirmed'
    """,
    (
        data["date"],
        data["time"]
    )
)


        existing = cursor.fetchone()



        if existing:

            conn.close()

            return jsonify({

                "error":
                "This time is already reserved. Please choose another time."

            }),409



        # Create booking

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
                payment_status,
                status
            )

            VALUES (?,?,?,?,?,?,?,?,?)

            """,

            (

                data["name"],
                data["email"],
                data["phone"],
                data["lesson_type"],
                data["package"],
                data["date"],
                data["time"],
                "pending",
                "pending"

            )
        )


        booking_id = cursor.lastrowid


        conn.commit()

        conn.close()



        return jsonify({

            "success": True,

            "booking_id": booking_id

        })



    except Exception as e:


        print(
            "BOOKING ERROR:",
            e
        )


        return jsonify({

            "error": str(e)

        }),500





# =====================================
# CALENDAR BOOKINGS
# =====================================

@booking_bp.route("/bookings")
def get_bookings():


    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT lesson_date, lesson_time
        FROM bookings
        WHERE status='confirmed'
        """
    )


    rows = cursor.fetchall()


    conn.close()



    return jsonify([

        {
            "title":"Booked",

            "start":
            f"{row['lesson_date']}T{row['lesson_time']}"
        }

        for row in rows

    ])





# =====================================
# AVAILABLE SLOT CHECK
# =====================================

@booking_bp.route("/booked-slots")
def booked_slots():


    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT lesson_date, lesson_time
        FROM bookings
        WHERE status IN ('pending','confirmed')
        """
    )


    rows = cursor.fetchall()


    conn.close()



    return jsonify([

        {
            "date": row["lesson_date"],

            "time": row["lesson_time"]
        }

        for row in rows

    ])


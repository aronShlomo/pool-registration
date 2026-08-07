from flask import Blueprint, request, jsonify

from database import get_db_connection

from email_service import (
    send_booking_confirmation,
    send_admin_notification
)


booking_bp = Blueprint(
    "booking",
    __name__
)



# =====================================
# CREATE BOOKING
# =====================================

@booking_bp.route("/create-booking", methods=["POST"])
def create_booking():

    conn = None

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,
                "error": "No booking data received"

            }), 400



        lesson_date = (
            data.get("lesson_date")
            or data.get("date")
        )


        lesson_time = (
            data.get("lesson_time")
            or data.get("time")
        )



        required = {

            "name": data.get("name"),

            "email": data.get("email"),

            "phone": data.get("phone"),

            "lesson_type": data.get("lesson_type"),

            "package": data.get("package"),

            "price": data.get("price"),

            "lesson_date": lesson_date,

            "lesson_time": lesson_time

        }



        for key, value in required.items():

            if not value:

                return jsonify({

                    "success": False,

                    "error": f"Missing {key}"

                }),400




        conn = get_db_connection()

        cursor = conn.cursor()



        # ==============================
        # CHECK SLOT
        # ==============================

        cursor.execute(
            """
            SELECT id
            FROM bookings
            WHERE lesson_date = ?
            AND lesson_time = ?
            AND status IN ('pending','confirmed')
            """,
            (
                lesson_date,
                lesson_time
            )
        )


        existing = cursor.fetchone()


        if existing:

            conn.close()

            return jsonify({

                "success":False,

                "error":
                "This time is already reserved. Please choose another time."

            }),409




        # ==============================
        # CREATE BOOKING
        # ==============================

        cursor.execute(
            """
            INSERT INTO bookings
            (
                name,
                email,
                phone,
                lesson_type,
                package,
                price,
                lesson_date,
                lesson_time,
                payment_method,
                payment_status,
                status
            )

            VALUES (?,?,?,?,?,?,?,?,?,?,?)

            """,

            (

                data["name"],

                data["email"],

                data["phone"],

                data["lesson_type"],

                data["package"],

                data["price"],

                lesson_date,

                lesson_time,

                "cash_or_zelle",

                "pending",

                "pending"

            )
        )


        booking_id = cursor.lastrowid


        conn.commit()



        # ==============================
        # GET BOOKING
        # ==============================

        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE id = ?
            """,
            (
                booking_id,
            )
        )


        booking = cursor.fetchone()


        conn.close()

        conn = None




        # ==============================
        # SEND EMAILS
        # ==============================

        try:

            print("SENDING CUSTOMER EMAIL...")


            customer_sent = send_booking_confirmation(

                booking["email"],

                booking["name"],

                booking["lesson_type"],

                booking["package"],

                booking["lesson_date"],

                booking["lesson_time"],

                booking["payment_status"],

                booking["price"]

            )


            print(
                "CUSTOMER EMAIL:",
                customer_sent
            )



            print("SENDING ADMIN EMAIL...")


            admin_sent = send_admin_notification(
                booking
            )


            print(
                "ADMIN EMAIL:",
                admin_sent
            )


        except Exception as email_error:


            print(
                "EMAIL ERROR:",
                repr(email_error)
            )





        return jsonify({

            "success":True,

            "booking_id":booking_id,

            "message":
            """
            Lesson reserved successfully!
            We accept cash or Zelle payments.
            Please pay when you arrive for your swimming lesson.
            """

        })




    except Exception as e:


        if conn:

            conn.rollback()


        print(
            "BOOKING ERROR:",
            repr(e)
        )


        return jsonify({

            "success":False,

            "error":str(e)

        }),500



    finally:


        if conn:

            conn.close()







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
        WHERE status IN ('pending','confirmed')
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
# BOOKED SLOTS
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

            "date":row["lesson_date"],

            "time":row["lesson_time"]

        }

        for row in rows

    ])
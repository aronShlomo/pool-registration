from flask import Blueprint, request, jsonify
import stripe

from config import Config
from database import get_db_connection

from email_service import (
    send_booking_confirmation,
    send_admin_notification
)


payment_bp = Blueprint(
    "payment",
    __name__
)


stripe.api_key = Config.STRIPE_SECRET_KEY



# =====================================
# CREATE STRIPE CHECKOUT
# =====================================

@payment_bp.route(
    "/create-checkout-session",
    methods=["POST"]
)
def create_checkout_session():

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "error":"No JSON received"
            }),400



        booking_id = data.get(
            "booking_id"
        )


        if not booking_id:

            return jsonify({
                "error":"Booking ID missing"
            }),400



        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE id=?
            """,
            (booking_id,)
        )


        booking = cursor.fetchone()

        conn.close()



        if not booking:

            return jsonify({
                "error":"Booking not found"
            }),404



        price = Config.LESSON_PRICES[
            booking["lesson_type"]
        ][
            booking["package"]
        ]



        session = stripe.checkout.Session.create(

            payment_method_types=[
                "card"
            ],

            mode="payment",


            customer_email=
                booking["email"],


            line_items=[

                {

                    "price_data":{

                        "currency":
                            Config.CURRENCY,


                        "product_data":{

                            "name":
                            f"{booking['lesson_type']} - {booking['package']}"

                        },


                        "unit_amount":
                            price

                    },


                    "quantity":1

                }

            ],


            metadata={

                "booking_id":
                    str(booking_id)

            },


            success_url=
                f"{Config.DOMAIN}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",


            cancel_url=
                f"{Config.DOMAIN}/payment-cancel"

        )



        return jsonify({

            "checkout_url":
                session.url

        })



    except Exception as e:

        print(
            "STRIPE ERROR:",
            e
        )


        return jsonify({

            "error":
                str(e)

        }),500




# =====================================
# TEST PAYMENT SUCCESS (NO STRIPE)
# =====================================

@payment_bp.route("/test-payment-success/<int:booking_id>")
def test_payment_success(booking_id):

    from email_service import (
        send_booking_confirmation,
        send_admin_notification
    )


    conn = get_db_connection()

    cursor = conn.cursor()


    # Confirm booking manually

    cursor.execute(
        """
        UPDATE bookings

        SET

        payment_status = 'paid',

        status = 'confirmed',

        stripe_payment_id = 'TEST_PAYMENT'

        WHERE id = ?

        """,
        (
            booking_id,
        )
    )


    conn.commit()



    # Get booking information

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



    if not booking:

        return "Booking not found"



    try:


        print("Sending customer confirmation email...")


        send_booking_confirmation(

            booking["email"],

            booking["name"],

            booking["lesson_type"],

            booking["package"],

            booking["lesson_date"],

            booking["lesson_time"]

        )



        print("Sending admin notification...")


        send_admin_notification(
            booking
        )


        print("ALL EMAILS SENT")



        return """

        <h1>TEST PAYMENT SUCCESS</h1>

        <p>Booking confirmed.</p>

        <p>Customer email sent.</p>

        <p>Admin email sent.</p>

        <a href="/">Return Home</a>

        """



    except Exception as e:


        print(
            "EMAIL ERROR:",
            repr(e)
        )


        return f"""

        <h1>Email Error</h1>

        <p>{e}</p>

        """




# =====================================
# PAYMENT SUCCESS
# =====================================

@payment_bp.route(
    "/payment-success"
)
def payment_success():


    session_id = request.args.get(
        "session_id"
    )


    if not session_id:

        return "Invalid payment"



    try:

        session = stripe.checkout.Session.retrieve(
            session_id
        )


        if session.payment_status != "paid":

            return "Payment not completed"



        booking_id = session.metadata["booking_id"]



        conn = get_db_connection()

        cursor = conn.cursor()



        cursor.execute(
            """
            UPDATE bookings

            SET
            payment_status='paid',
            status='confirmed',
            stripe_payment_id=?

            WHERE id=?

            """,

            (
                session.id,
                booking_id
            )

        )


        conn.commit()



        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE id=?
            """,
            (booking_id,)
        )


        booking = cursor.fetchone()



        conn.close()



        # Send emails

        send_booking_confirmation(

            booking["email"],

            booking["name"],

            booking["lesson_type"],

            booking["package"],

            booking["lesson_date"],

            booking["lesson_time"]

        )


        send_admin_notification(
            booking
        )



        return """

        <h1>
        Payment Successful!
        </h1>

        <p>
        Your swimming lesson is confirmed.
        </p>

        <a href="/">
        Return Home
        </a>

        """



    except Exception as e:


        print(
            "PAYMENT SUCCESS ERROR:",
            e
        )


        return "Payment processing error"





# =====================================
# PAYMENT CANCEL
# =====================================

@payment_bp.route(
    "/payment-cancel"
)
def payment_cancel():

    return """

    <h1>
    Payment Cancelled
    </h1>

    <p>
    You can return and select another time.
    </p>

    <a href="/">
    Back
    </a>

    """

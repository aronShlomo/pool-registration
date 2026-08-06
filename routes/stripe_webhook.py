from flask import Blueprint, request, jsonify
import stripe

from config import Config
from database import get_db_connection

from email_service import (
    send_booking_confirmation,
    send_admin_notification
)


# =====================================
# Stripe Webhook Blueprint
# =====================================

webhook_bp = Blueprint(
    "webhook",
    __name__
)


stripe.api_key = Config.STRIPE_SECRET_KEY



# =====================================
# Stripe Webhook Route
# =====================================

@webhook_bp.route(
    "/stripe-webhook",
    methods=["POST"]
)
def stripe_webhook():

    payload = request.data

    sig_header = request.headers.get(
        "Stripe-Signature"
    )


    try:

        event = stripe.Webhook.construct_event(

            payload,

            sig_header,

            Config.STRIPE_WEBHOOK_SECRET

        )


    except ValueError:

        return jsonify({
            "error": "Invalid payload"
        }), 400


    except stripe.error.SignatureVerificationError:

        return jsonify({
            "error": "Invalid signature"
        }), 400



    # =================================
    # PAYMENT SUCCESS
    # =================================

    if event["type"] == "checkout.session.completed":


        session = event["data"]["object"]


        booking_id = session["metadata"].get(
            "booking_id"
        )


        if not booking_id:

            return jsonify({
                "error": "Missing booking id"
            }), 400



        conn = get_db_connection()

        cursor = conn.cursor()



        # Update booking payment status

        cursor.execute(
            """
            UPDATE bookings

            SET

                payment_status = 'paid',

                status = 'confirmed',

                stripe_payment_id = ?

            WHERE id = ?

            """,
            (
                session.get("payment_intent"),

                booking_id
            )
        )



        conn.commit()



        # Get booking details

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



        # =================================
        # SEND EMAILS
        # =================================

        if booking:


            # Customer confirmation

            send_booking_confirmation(

                booking["email"],

                booking["name"],

                booking["lesson_type"],

                booking["package"],

                booking["lesson_date"],

                booking["lesson_time"]

            )



            # Admin notification

            send_admin_notification(

                booking["name"],

                booking["lesson_type"],

                booking["lesson_date"],

                booking["lesson_time"]

            )



    return jsonify({

        "received": True

    })
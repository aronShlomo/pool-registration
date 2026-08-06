from flask import Blueprint, request, jsonify
import stripe

from config import Config
from database import get_db_connection

from email_service import (
    send_booking_confirmation,
    send_admin_notification
)


stripe_bp = Blueprint("stripe", __name__)

stripe.api_key = Config.STRIPE_SECRET_KEY


@stripe_bp.route("/stripe-webhook", methods=["POST"])
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


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400



    # =================================
    # PAYMENT COMPLETED
    # PUT IT HERE
    # =================================

    if event["type"] == "checkout.session.completed":


        session = event["data"]["object"]


        booking_id = session["metadata"]["booking_id"]



        conn = get_db_connection()

        cursor = conn.cursor()



        # Update payment status

        cursor.execute(
            """
            UPDATE bookings

            SET 
            payment_status = 'paid',
            status = 'confirmed'

            WHERE id = ?

            """,
            (booking_id,)
        )


        conn.commit()



        # Get booking information

        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,)
        )


        booking = cursor.fetchone()


        conn.close()



        # Send emails

        if booking:


            send_booking_confirmation(

                booking["email"],

                booking["name"],

                booking["lesson_type"],

                booking["package"],

                booking["lesson_date"],

                booking["lesson_time"]

            )


            send_admin_notification(

                booking["name"],

                booking["lesson_type"],

                booking["lesson_date"],

                booking["lesson_time"]

            )



    return jsonify({
        "received": True
    })
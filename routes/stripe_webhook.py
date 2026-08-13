from flask import Blueprint, request, jsonify
import stripe

from config import Config
from database import get_db_connection

from email_service import (
    send_booking_confirmation,
    send_admin_notification
)


webhook_bp = Blueprint(
    "webhook",
    __name__
)


stripe.api_key = Config.STRIPE_SECRET_KEY



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
            "error":"Invalid payload"
        }),400


    except stripe.error.SignatureVerificationError:

        return jsonify({
            "error":"Invalid signature"
        }),400



    print(
        "STRIPE EVENT:",
        event["type"]
    )



    if event["type"] == "checkout.session.completed":


        session = event["data"]["object"]


        booking_id = session.get(
            "metadata",
            {}
        ).get(
            "booking_id"
        )


        if not booking_id:

            return jsonify({
                "error":"Booking ID missing"
            }),400



        conn = get_db_connection()

        cursor = conn.cursor()



        # Find booking first

        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE id=?
            """,
            (
                booking_id,
            )
        )


        booking = cursor.fetchone()



        if not booking:

            conn.close()

            return jsonify({
                "error":"Booking not found"
            }),404



        # Prevent duplicate confirmations

        if booking["status"] == "confirmed":

            conn.close()

            return jsonify({
                "received":True
            })



        # Confirm booking

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

                session.get(
                    "payment_intent",
                    session.get("id")
                ),

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

            (
                booking_id,
            )

        )


        booking = cursor.fetchone()


        conn.close()



        try:

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


            print(
                "EMAILS SENT"
            )


        except Exception as e:

            print(
                "EMAIL ERROR:",
                repr(e)
            )



    return jsonify({

        "received":True

    })


from flask import Blueprint, request, jsonify
import stripe

from config import Config
from database import get_db_connection


payment_bp = Blueprint("payment", __name__)

stripe.api_key = Config.STRIPE_SECRET_KEY



@payment_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():

    data = request.json


    booking_id = data.get("booking_id")


    if not booking_id:
        return jsonify({
            "error": "Booking ID missing"
        }), 400



    conn = get_db_connection()

    cursor = conn.cursor()


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



    if not booking:

        return jsonify({
            "error": "Booking not found"
        }), 404



    try:

        price = Config.LESSON_PRICES[
            booking["lesson_type"]
        ][
            booking["package"]
        ]



        session = stripe.checkout.Session.create(

            payment_method_types=[
                "card"
            ],


            line_items=[

                {

                    "price_data": {

                        "currency": Config.CURRENCY,


                        "product_data": {

                            "name":
                            f'{booking["lesson_type"]} - {booking["package"]}',

                            "description":
                            "Millrod Swim Academy Swimming Lesson"

                        },


                        "unit_amount": price

                    },


                    "quantity": 1

                }

            ],


            mode="payment",


            metadata={

                "booking_id": str(booking_id)

            },


            success_url=
            f"{Config.DOMAIN}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",


            cancel_url=
            f"{Config.DOMAIN}/payment-cancel"

        )



        return jsonify({

            "checkout_url": session.url

        })



    except Exception as e:


        return jsonify({

            "error": str(e)

        }), 500





@payment_bp.route("/payment-success")
def payment_success():

    return """
    <h1>Payment Successful!</h1>
    <p>Your swimming lesson has been booked.</p>
    """





@payment_bp.route("/payment-cancel")
def payment_cancel():

    return """
    <h1>Payment Cancelled</h1>
    <p>Your booking was not completed.</p>
    """
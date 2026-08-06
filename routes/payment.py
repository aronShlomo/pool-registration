from flask import Blueprint, request, jsonify
import stripe

from config import Config
from database import get_db_connection


payment_bp = Blueprint("payment", __name__)

stripe.api_key = Config.STRIPE_SECRET_KEY



@payment_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():

    try:

        data = request.get_json()

        print("========== CHECKOUT DEBUG ==========")
        print("Received data:", data)


        if not data:
            return jsonify({
                "error": "No JSON received"
            }), 400


        booking_id = data.get("booking_id")

        print("Booking ID:", booking_id)


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


        print("Booking found:", booking)


        if not booking:
            return jsonify({
                "error": "Booking not found"
            }), 404



        lesson_type = booking["lesson_type"]
        package = booking["package"]


        print("Lesson type:", lesson_type)
        print("Package:", package)



        price = Config.LESSON_PRICES[lesson_type][package]


        print("Price:", price)



        session = stripe.checkout.Session.create(

            payment_method_types=[
                "card"
            ],

            mode="payment",

            line_items=[
                {
                    "price_data": {

                        "currency": Config.CURRENCY,

                        "product_data": {
                            "name": f"{lesson_type} - {package}"
                        },

                        "unit_amount": price
                    },

                    "quantity": 1
                }
            ],

            metadata={
                "booking_id": str(booking_id)
            },

            success_url=f"{Config.DOMAIN}/payment-success",

            cancel_url=f"{Config.DOMAIN}/payment-cancel"

        )


        print("Stripe session created:", session.id)


        return jsonify({
            "checkout_url": session.url
        })


    except Exception as e:

        print("========== ERROR ==========")
        print(repr(e))

        return jsonify({
            "error": repr(e)
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
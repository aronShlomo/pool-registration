from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for
)

from database import get_db_connection
from config import Config
from email_service import send_payment_options_email

from datetime import datetime


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)




# =====================================
# CHECK LOGIN
# =====================================

def admin_required():

    return session.get(
        "admin_logged_in",
        False
    )





# =====================================
# LOGIN
# =====================================

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():

    # Already logged in? Go straight to dashboard.
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == Config.ADMIN_USERNAME
            and password == Config.ADMIN_PASSWORD
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.admin_dashboard"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# =====================================
# LOGOUT
# =====================================

@admin_bp.route("/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect("/")





# =====================================
# DASHBOARD
# =====================================

@admin_bp.route("/")
def admin_dashboard():


    if not admin_required():

        return redirect(
            url_for(
                "admin.admin_login"
            )
        )



    conn = get_db_connection()

    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT *
        FROM bookings
        ORDER BY lesson_date, lesson_time
        """
    )


    bookings = cursor.fetchall()



    today = datetime.now().strftime(
        "%Y-%m-%d"
    )



    cursor.execute(
        """
        SELECT COUNT(*)
        FROM bookings
        WHERE lesson_date=?
        AND status='confirmed'
        """,
        (today,)
    )


    today_lessons = cursor.fetchone()[0]




    cursor.execute(
        """
        SELECT COUNT(*)
        FROM bookings
        WHERE payment_status='pending'
        """
    )


    pending_payments = cursor.fetchone()[0]




    cursor.execute(
        """
        SELECT COUNT(*)
        FROM bookings
        WHERE status='confirmed'
        """
    )


    confirmed_lessons = cursor.fetchone()[0]




    # Sum revenue of paid bookings (price may be stored like '$80' or '80')

    cursor.execute(
        """
        SELECT COALESCE(SUM(CAST(REPLACE(price, '$', '') AS REAL)), 0)
        FROM bookings
        WHERE payment_status='paid'
        """
    )

    revenue_value = cursor.fetchone()[0] or 0

    # Format to two decimal places (dollars)
    try:
        revenue = f"{float(revenue_value):.2f}"
    except Exception:
        revenue = "0.00"



    conn.close()



    return render_template(
        "admin.html",

        bookings=bookings,

        today_lessons=today_lessons,

        pending_payments=pending_payments,

        confirmed_lessons=confirmed_lessons,

        revenue=revenue
    )






# =====================================
# GET BOOKING
# =====================================

@admin_bp.route(
    "/booking/<int:id>"
)
def get_booking(id):


    if not admin_required():

        return jsonify({
            "error":"Unauthorized"
        }),401



    conn = get_db_connection()

    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE id=?
        """,
        (id,)
    )



    booking = cursor.fetchone()


    conn.close()



    if not booking:

        return jsonify({
            "error":"Booking not found"
        }),404



    return jsonify(
        dict(booking)
    )






# =====================================
# UPDATE STATUS
# =====================================

@admin_bp.route(
    "/update-status/<int:id>",
    methods=["POST"]
)
def update_status(id):


    if not admin_required():

        return jsonify({
            "error":"Unauthorized"
        }),401



    data = request.json


    status = data.get(
        "status"
    )



    if status not in [
        "pending",
        "confirmed",
        "cancelled"
    ]:

        return jsonify({
            "error":"Invalid status"
        }),400



    conn = get_db_connection()

    cursor = conn.cursor()



    cursor.execute(
        """
        UPDATE bookings

        SET status=?

        WHERE id=?

        """,
        (
            status,
            id
        )
    )


    conn.commit()

    # If booking was confirmed, send payment options email to customer
    if status == 'confirmed':
        try:
            cursor.execute(
                """
                SELECT *
                FROM bookings
                WHERE id=?
                """,
                (id,)
            )

            booking = cursor.fetchone()

            if booking:
                # convert sqlite row to dict if necessary
                send_payment_options_email(dict(booking))
        except Exception as e:
            print("Error sending payment options email:", e)

    conn.close()


    return jsonify({
        "success":True
    })





# =====================================
# CANCEL BOOKING
# =====================================

@admin_bp.route(
    "/delete/<int:id>",
    methods=["DELETE"]
)
def delete_booking(id):


    if not admin_required():

        return jsonify({
            "error":"Unauthorized"
        }),401



    conn = get_db_connection()

    cursor = conn.cursor()



    cursor.execute(
        """
        UPDATE bookings

        SET status='cancelled'

        WHERE id=?

        """,
        (id,)
    )



    conn.commit()

    conn.close()



    return jsonify({
        "success":True
    })

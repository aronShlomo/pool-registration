from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from database import get_db_connection
from config import Config
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# =====================================
# Admin Login
# =====================================

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")
        
        print("Entered username:", repr(username))
        print("Entered password:", repr(password))
        print("Expected username:", repr(Config.ADMIN_USERNAME))
        print("Expected password:", repr(Config.ADMIN_PASSWORD))


        if (
            username == Config.ADMIN_USERNAME
            and password == Config.ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin.admin_dashboard")
            )


        return render_template(
            "login.html",
            error="Invalid username or password"
        )


    return render_template("login.html")


# =====================================
# Admin Logout
# =====================================

@admin_bp.route("/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )


    return redirect(
        url_for("admin.admin_login")
    )


# =====================================
# Admin Dashboard
# =====================================

@admin_bp.route("/")
def admin_dashboard():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin.admin_login")
        )

    conn = get_db_connection()
    cursor = conn.cursor()


    # All bookings

    cursor.execute("""
        SELECT *
        FROM bookings
        ORDER BY lesson_date, lesson_time
    """)

    bookings = cursor.fetchall()



    # Today's lessons

    today = datetime.now().strftime("%Y-%m-%d")


    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE lesson_date = ?
        AND status = 'confirmed'
    """, (today,))


    today_lessons = cursor.fetchone()[0]



    # Pending payments

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE payment_status = 'pending'
    """)


    pending_payments = cursor.fetchone()[0]



    # Confirmed lessons

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'confirmed'
    """)


    confirmed_lessons = cursor.fetchone()[0]



    # Revenue

    cursor.execute("""
        SELECT SUM(
            CASE
                WHEN payment_status = 'paid'
                THEN 1
                ELSE 0
            END
        )
        FROM bookings
    """)


    revenue = cursor.fetchone()[0] or 0



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
# View Booking Details
# =====================================

@admin_bp.route("/booking/<int:id>")
def get_booking(id):
    if not session.get("admin_logged_in"):

        return jsonify({
            "error": "Unauthorized"
        }), 401
    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE id = ?
        """,
        (id,)
    )


    booking = cursor.fetchone()


    conn.close()



    if not booking:

        return jsonify({

            "error":"Booking not found"

        }),404



    return jsonify(dict(booking))





# =====================================
# Update Status
# =====================================

@admin_bp.route("/update-status/<int:id>", methods=["POST"])
def update_status(id):
    if not session.get("admin_logged_in"):

        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.json


    status = data.get("status")



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

        SET status = ?

        WHERE id = ?

        """,
        (
            status,
            id
        )
    )


    conn.commit()

    conn.close()



    return jsonify({

        "success":True

    })





# =====================================
# Delete Booking
# =====================================

@admin_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_booking(id):
    if not session.get("admin_logged_in"):

        return jsonify({
            "error": "Unauthorized"
        }), 401

    conn = get_db_connection()

    cursor = conn.cursor()



    cursor.execute(
        """
        DELETE FROM bookings
        WHERE id = ?
        """,
        (id,)
    )



    conn.commit()

    conn.close()



    return jsonify({

        "success":True

    })
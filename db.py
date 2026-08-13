import sqlite3

DB_PATH = "bookings.db"


# ==========================
# DATABASE CONNECTION
# ==========================

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================
# CREATE BOOKING
# ==========================

def create_booking(data):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bookings (
            name, email, phone, lesson_type, package,
            lesson_date, lesson_time, price, status,
            payment_method, payment_status, stripe_payment_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
    """, (
        data["name"],
        data["email"],
        data.get("phone"),
        data["lesson_type"],
        data["package"],
        data["lesson_date"],
        data["lesson_time"],
        data["price"],
        data.get("payment_method", "none"),
        data.get("payment_status", "pending"),
        data.get("stripe_payment_id")
    ))

    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id


# ==========================
# GET BOOKING
# ==========================

def get_booking(booking_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return dict(row)  # row_factory makes this easy


# ==========================
# UPDATE BOOKING STATUS
# ==========================

def update_booking_status(booking_id, status):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        (status, booking_id)
    )

    conn.commit()
    conn.close()

import sqlite3

from config import Config
from datetime import datetime, timedelta



DATABASE = Config.DATABASE



# ==========================
# DATABASE CONNECTION
# ==========================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def remove_expired_pending_bookings():

    conn = get_db_connection()

    cursor = conn.cursor()


    expired_time = (
        datetime.now()
        - timedelta(minutes=30)
    )


    cursor.execute(
        """
        DELETE FROM bookings
        WHERE status = 'pending'
        AND payment_status = 'pending'
        AND created_at < ?
        """,
        (
            expired_time,
        )
    )


    conn.commit()

    conn.close()


# ==========================
# INITIALIZE DATABASE
# ==========================

def init_database():

    conn = get_db_connection()

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Customer information

        name TEXT NOT NULL,

        email TEXT NOT NULL,

        phone TEXT,


        -- Lesson information

        lesson_type TEXT NOT NULL,

        package TEXT NOT NULL,


        -- Schedule

        lesson_date TEXT NOT NULL,

        lesson_time TEXT NOT NULL,


        -- Payment

        payment_status TEXT DEFAULT 'pending',

        stripe_payment_id TEXT,


        -- Booking status

        status TEXT DEFAULT 'pending',


        -- Reminder system

        reminder_sent INTEGER DEFAULT 0,


        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)



    # ==========================
    # DATABASE MIGRATIONS
    # ==========================

    migrations = {

        "payment_status": "TEXT DEFAULT 'pending'",

        "stripe_payment_id": "TEXT",

        "status": "TEXT DEFAULT 'pending'",

        "reminder_sent": "INTEGER DEFAULT 0"

    }



    for column, definition in migrations.items():

        try:

            cursor.execute(
                f"""
                ALTER TABLE bookings
                ADD COLUMN {column} {definition}
                """
            )

        except sqlite3.OperationalError:

            pass



    conn.commit()

    conn.close()



# ==========================
# COMPATIBILITY
# ==========================

def init_db():

    init_database()


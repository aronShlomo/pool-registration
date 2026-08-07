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



# ==========================
# REMOVE EXPIRED PENDING BOOKINGS
# ==========================

def remove_expired_pending_bookings():

    conn = get_db_connection()

    cursor = conn.cursor()


    expired_time = (
        datetime.now()
        - timedelta(minutes=30)
    ).strftime("%Y-%m-%d %H:%M:%S")


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


    cursor.execute(
        """

        CREATE TABLE IF NOT EXISTS bookings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,


            name TEXT NOT NULL,

            email TEXT NOT NULL,

            phone TEXT,


            lesson_type TEXT NOT NULL,

            package TEXT NOT NULL,


            lesson_date TEXT NOT NULL,

            lesson_time TEXT NOT NULL,
            
            price TEXT,


            payment_method TEXT DEFAULT 'none',

            payment_status TEXT DEFAULT 'pending',

            stripe_payment_id TEXT,
            


            status TEXT DEFAULT 'pending',


            reminder_sent INTEGER DEFAULT 0,


            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """
    )



    # ==========================
    # SAFE MIGRATIONS
    # ==========================

    cursor.execute(
        "PRAGMA table_info(bookings)"
    )


    existing_columns = [

        column[1]

        for column in cursor.fetchall()

    ]



    migrations = {

        "payment_method":
        "TEXT DEFAULT 'none'",


        "payment_status":
        "TEXT DEFAULT 'pending'",


        "stripe_payment_id":
        "TEXT",


        "status":
        "TEXT DEFAULT 'pending'",


        "reminder_sent":
        "INTEGER DEFAULT 0",
        
        "price": "TEXT"

        
        

    }



    for column, definition in migrations.items():


        if column not in existing_columns:


            cursor.execute(

                f"""

                ALTER TABLE bookings

                ADD COLUMN {column} {definition}

                """

            )


            print(
                f"Added column: {column}"
            )



    conn.commit()

    conn.close()



# ==========================
# COMPATIBILITY
# ==========================

def init_db():

    init_database()
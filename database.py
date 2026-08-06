import sqlite3

from config import Config


DATABASE = Config.DATABASE



def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn



def init_db():

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


    # Add reminder column if database already existed
    try:

        cursor.execute("""
            ALTER TABLE bookings
            ADD COLUMN reminder_sent INTEGER DEFAULT 0
        """)

    except sqlite3.OperationalError:

        # Column already exists
        pass



    conn.commit()

    conn.close()



def create_booking_table():

    init_db()
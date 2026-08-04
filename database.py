import sqlite3

def create_database():

    conn = sqlite3.connect("pool.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        student_name TEXT,
        booked INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


create_database()


conn = sqlite3.connect("pool.db")
cursor = conn.cursor()

schedule = [
    ("2026-09-01", "4:00 PM"),
    ("2026-09-01", "5:00 PM"),
    ("2026-09-01", "6:00 PM"),
    ("2026-09-02", "4:00 PM"),
]

for item in schedule:
    cursor.execute(
        """
        INSERT INTO schedules(date,time)
        VALUES (?,?)
        """,
        item
    )

conn.commit()
conn.close()
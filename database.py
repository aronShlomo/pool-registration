import sqlite3

conn = sqlite3.connect("pool.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_date TEXT NOT NULL,
    lesson_time TEXT NOT NULL,
    class_name TEXT,
    capacity INTEGER DEFAULT 1,
    booked INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("Schedule table created")
import sqlite3
from datetime import datetime, timedelta


conn = sqlite3.connect("pool.db")

cursor = conn.cursor()


# Remove old schedule entries
# Keep this only for testing
# cursor.execute("DELETE FROM schedule")


# Get today's date
today = datetime.now().date()

# Maximum booking date (30 days ahead)
max_date = today + timedelta(days=30)


hours = [
    "4:00 PM",
    "5:00 PM",
    "6:00 PM"
]


schedule = []


current_date = today


while current_date <= max_date:

    # Skip Sunday
    if current_date.weekday() != 6:

        for hour in hours:

            if hour == "6:00 PM":
                class_name = "Kids Intermediate"
            else:
                class_name = "Kids Beginner"


            schedule.append(
                (
                    current_date.strftime("%Y-%m-%d"),
                    hour,
                    class_name,
                    0   # Available
                )
            )


    current_date += timedelta(days=1)



cursor.executemany(
"""
INSERT INTO schedule
(
    lesson_date,
    lesson_time,
    class_name,
    booked
)

VALUES (?,?,?,?)

""",
schedule
)


conn.commit()

conn.close()


print(f"Added {len(schedule)} swimming schedule slots")
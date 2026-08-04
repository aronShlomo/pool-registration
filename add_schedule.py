import sqlite3


conn = sqlite3.connect("pool.db")

cursor = conn.cursor()


schedule = [

("2026-08-10", "4:00 PM", "Kids Beginner"),
("2026-08-10", "5:00 PM", "Kids Beginner"),
("2026-08-10", "6:00 PM", "Kids Intermediate"),

("2026-08-11", "4:00 PM", "Kids Beginner"),
("2026-08-11", "5:00 PM", "Kids Intermediate")

]


cursor.executemany(
"""
INSERT INTO schedule
(lesson_date, lesson_time, class_name)
VALUES (?,?,?)
""",
schedule
)


conn.commit()

conn.close()


print("Schedule added")
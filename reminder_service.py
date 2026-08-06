from datetime import datetime, timedelta

from database import get_db_connection

from email_service import send_reminder_email



# =====================================
# SEND LESSON REMINDERS
# =====================================

def send_lesson_reminders():

    try:


        tomorrow = (
            datetime.now()
            + timedelta(days=1)
        ).strftime("%Y-%m-%d")



        conn = get_db_connection()

        cursor = conn.cursor()



        cursor.execute(
            """
            SELECT *

            FROM bookings

            WHERE lesson_date = ?

            AND status = 'confirmed'

            AND reminder_sent = 0

            """,

            (
                tomorrow,
            )
        )



        bookings = cursor.fetchall()



        for booking in bookings:



            success = send_reminder_email(

                booking["email"],

                booking["name"],

                booking["lesson_type"],

                booking["lesson_date"],

                booking["lesson_time"]

            )



            if success:


                cursor.execute(
                    """
                    UPDATE bookings

                    SET reminder_sent = 1

                    WHERE id = ?

                    """,

                    (
                        booking["id"],
                    )

                )



        conn.commit()

        conn.close()



        print(
            "REMINDER CHECK COMPLETED"
        )



    except Exception as e:


        print(
            "REMINDER SERVICE ERROR:",
            repr(e)
        )

import resend

from config import Config


resend.api_key = Config.RESEND_API_KEY



def send_booking_confirmation(
    customer_email,
    customer_name,
    lesson_type,
    package,
    lesson_date,
    lesson_time
):

    resend.Emails.send({

        "from": "Millrod Swim Academy <info@millrodswim.com>",

        "to": [
            customer_email
        ],

        "subject":
        "Your Swimming Lesson Booking Confirmation",

        "html": f"""

        <h2>
        🏊 Millrod Swim Academy
        </h2>


        <p>
        Hello {customer_name},
        </p>


        <p>
        Your swimming lesson has been confirmed.
        </p>


        <h3>
        Lesson Details:
        </h3>


        <p>
        <b>Lesson:</b> {lesson_type}
        </p>


        <p>
        <b>Package:</b> {package}
        </p>


        <p>
        <b>Date:</b> {lesson_date}
        </p>


        <p>
        <b>Time:</b> {lesson_time}
        </p>


        <br>


        <p>
        Thank you for choosing Millrod Swim Academy!
        </p>


        """

    })




def send_admin_notification(
    customer_name,
    lesson_type,
    lesson_date,
    lesson_time
):

    resend.Emails.send({

        "from": "Millrod Swim Academy <info@millrodswim.com>",

        "to": [
            Config.OWNER_EMAIL
        ],

        "subject":
        "New Swimming Lesson Booking",

        "html": f"""

        <h2>
        New Booking Received
        </h2>


        <p>
        Student: {customer_name}
        </p>


        <p>
        Lesson: {lesson_type}
        </p>


        <p>
        Date: {lesson_date}
        </p>


        <p>
        Time: {lesson_time}
        </p>

        """

    })
    
    def send_reminder_email(
    customer_email,
    customer_name,
    lesson_type,
    lesson_date,
    lesson_time
):


    resend.Emails.send({

        "from":
        "Millrod Swim Academy <info@millrodswim.com>",


        "to":
        [
            customer_email
        ],


        "subject":
        "Reminder: Swimming Lesson Tomorrow",


        "html":
        f"""

        <h2>
        🏊 Millrod Swim Academy
        </h2>


        <p>
        Hello {customer_name},
        </p>


        <p>
        This is a reminder that your swimming lesson is tomorrow.
        </p>


        <p>
        <b>Lesson:</b> {lesson_type}
        </p>


        <p>
        <b>Date:</b> {lesson_date}
        </p>


        <p>
        <b>Time:</b> {lesson_time}
        </p>


        <p>
        We look forward to seeing you!
        </p>

        """

    })
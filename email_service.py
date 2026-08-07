import resend
import os
import tempfile
import base64

from config import Config

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet



# ==========================
# RESEND CONFIGURATION
# ==========================

if Config.RESEND_API_KEY:

    resend.api_key = Config.RESEND_API_KEY

else:

    print("WARNING: RESEND_API_KEY is missing")



EMAIL_FROM = Config.EMAIL_FROM





# ==========================
# CUSTOMER BOOKING EMAIL
# ==========================

def send_booking_confirmation(
    customer_email,
    customer_name,
    lesson_type,
    package,
    lesson_date,
    lesson_time,
    payment_status,
    price
    
):

    try:

        if payment_status == "paid":

            message = """
            Your payment has been received.
            Your swimming lesson is confirmed.
            """

            subject = (
                "Swimming Lesson Confirmed - Millrod Swim Academy"
            )

        else:

            message = """
            Your swimming lesson has been reserved.
            Payment is still pending.
            You can complete payment later.
            """

            subject = (
                "Swimming Lesson Reserved - Millrod Swim Academy"
            )



        response = resend.Emails.send({

            "from": EMAIL_FROM,

            "to": [
                customer_email
            ],

            "subject": subject,


            "html": f"""

            <h2>
            🏊 Millrod Swim Academy
            </h2>


            <p>
            Hello {customer_name},
            </p>


            <p>
            {message}
            </p>


            <h3>
            Lesson Details
            </h3>


            <p>
            <b>Lesson:</b>
            {lesson_type}
            </p>


            <p>
            <b>Package:</b>
            {package}
            </p>
                        
            <p>
            <b>Package:</b>
            {package}
            </p>


            <p>
            <b>Amount:</b>
            {price}
            </p>


            <p>
            <b>Date:</b>
            {lesson_date}
            </p>


            <p>
            <b>Time:</b>
            {lesson_time}
            </p>


            <p>
            <b>Date:</b>
            {lesson_date}
            </p>


            <p>
            <b>Time:</b>
            {lesson_time}
            </p>

          

            <br>

            <p>
            <b>Payment Status:</b>
            Payment pending - Please pay with cash or Zelle when you arrive.
            </p>

            <p>
            Thank you for choosing
            Millrod Swim Academy!
            </p>

            """

        })


        print(
            "CUSTOMER EMAIL SENT:",
            response
        )


        return True



    except Exception as e:

        print(
            "CUSTOMER EMAIL ERROR:",
            repr(e)
        )

        return False







# ==========================
# ADMIN NOTIFICATION EMAIL
# ==========================

def send_admin_notification(booking):

    pdf_file = None


    try:

        pdf_file = create_booking_pdf(
            booking
        )


        with open(
            pdf_file,
            "rb"
        ) as file:


            pdf_base64 = base64.b64encode(
                file.read()
            ).decode()



        response = resend.Emails.send({

            "from": EMAIL_FROM,


            "to": [
                Config.OWNER_EMAIL
            ],


            "subject":
            "New Swimming Lesson Booking",



            "html": f"""

            <h2>
            🏊 New Booking Received
            </h2>


            <p>
            A new swimming lesson reservation was created.
            </p>


            <hr>


            <p>
            <b>Student:</b>
            {booking["name"]}
            </p>


            <p>
            <b>Email:</b>
            {booking["email"]}
            </p>


            <p>
            <b>Phone:</b>
            {booking["phone"]}
            </p>


            <p>
            <b>Lesson:</b>
            {booking["lesson_type"]}
            </p>


            <p>
            <b>Package:</b>
            {booking["package"]}
            </p>


            <p>
            <b>Date:</b>
            {booking["lesson_date"]}
            </p>


            <p>
            <b>Time:</b>
            {booking["lesson_time"]}
            </p>


            <p>
            <b>Payment:</b>
            {booking["payment_status"]}
            </p>


            """,


            "attachments":[

                {

                    "filename":
                    "booking_information.pdf",


                    "content":
                    pdf_base64

                }

            ]

        })


        print(
            "ADMIN EMAIL SENT:",
            response
        )


        return True



    except Exception as e:


        print(
            "ADMIN EMAIL ERROR:",
            repr(e)
        )


        return False



    finally:


        if pdf_file and os.path.exists(pdf_file):

            os.remove(pdf_file)







# ==========================
# CREATE BOOKING PDF
# ==========================

def create_booking_pdf(booking):


    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )


    file_path = temp_file.name


    temp_file.close()



    document = SimpleDocTemplate(
        file_path,
        pagesize=letter
    )



    styles = getSampleStyleSheet()


    content = []


    amount = "Please contact Millrod Swim Academy for payment amount"


    if booking["package"] == "Single Lesson":
        amount = "$80"

    elif booking["package"] == "4 Lessons Package":
        amount = "$300"

    elif booking["package"] == "8 Lessons Package":
        amount = "$560"

    elif booking["package"] == "Monthly Program":
        amount = "$700"



    information=[

        "Millrod Swim Academy",

        "Swimming Lesson Booking Confirmation",

        "",

        f"Student: {booking['name']}",

        f"Email: {booking['email']}",

        f"Phone: {booking['phone']}",

        f"Lesson Type: {booking['lesson_type']}",

        f"Package: {booking['package']}",

        f"Date: {booking['lesson_date']}",

        f"Time: {booking['lesson_time']}",


        "----------------------------",


        "Payment Status: NOT PAID YET",

        f"Amount Due: {amount}",

        "Payment Method: Cash or Zelle",

        "",

        "Please pay when you arrive for your swimming lesson.",

    ]



    for item in information:


        content.append(

            Paragraph(
                item,
                styles["Normal"]
            )

        )


        content.append(
            Spacer(1,12)
        )



    document.build(
        content
    )



    return file_path







# ==========================
# REMINDER EMAIL
# ==========================

def send_reminder_email(
    customer_email,
    customer_name,
    lesson_type,
    lesson_date,
    lesson_time
):

    try:


        response = resend.Emails.send({

            "from": EMAIL_FROM,


            "to":[
                customer_email
            ],


            "subject":
            "Reminder: Swimming Lesson Tomorrow",


            "html": f"""

            <h2>
            🏊 Millrod Swim Academy
            </h2>


            <p>
            Hello {customer_name},
            </p>


            <p>
            This is a reminder that your swimming lesson
            is tomorrow.
            </p>


            <h3>
            Lesson Details
            </h3>


            <p>
            <b>Lesson:</b>
            {lesson_type}
            </p>


            <p>
            <b>Date:</b>
            {lesson_date}
            </p>


            <p>
            <b>Time:</b>
            {lesson_time}
            </p>


            <br>


            <p>
            We look forward to seeing you!
            </p>


            """

        })


        print(
            "REMINDER EMAIL SENT:",
            response
        )


        return True



    except Exception as e:


        print(
            "REMINDER EMAIL ERROR:",
            repr(e)
        )


        return False
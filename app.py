from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import uuid
import traceback
from xml.sax.saxutils import escape
import resend
import sqlite3
import base64
from datetime import datetime, timedelta


app = Flask(__name__)

from dotenv import load_dotenv
import os

load_dotenv()

OWNER_EMAIL = os.getenv("POOL_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
resend.api_key = os.getenv("RESEND_API_KEY")

print("POOL_EMAIL:", OWNER_EMAIL)
print("EMAIL_PASSWORD exists:", EMAIL_PASSWORD is not None)
print("RESEND_API_KEY exists:", os.getenv("RESEND_API_KEY") is not None)



@app.route("/")
def home():

    import sqlite3

    conn = sqlite3.connect("pool.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, lesson_date, lesson_time, class_name
        FROM schedule
        WHERE booked = 0
        ORDER BY lesson_date, lesson_time
    """)

    slots = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        slots=slots
    )
    
    
    

@app.route("/test")
def test():
    return "Flask is working!"



@app.route("/schedule")
def schedule():

    import sqlite3

    conn = sqlite3.connect("pool.db")
    cursor = conn.cursor()


    cursor.execute("""
        SELECT id, lesson_date, lesson_time, class_name, booked
        FROM schedule
    """)


    rows = cursor.fetchall()

    conn.close()


    events = []


    for row in rows:

        slot_id = row[0]
        date = row[1]
        time = row[2]
        class_name = row[3]
        booked = row[4]


        if booked == 1:

            color = "black"
            title = "Booked"
            available = False

        else:

            color = "green"
            title = class_name
            available = True



        events.append({

            "id": slot_id,

            "title": title,

            "start": f"{date}T{time}",

            "color": color,

            "extendedProps": {

                "available": available

            }

        })


    return events




def send_email(to_email, subject, body, attachment=None):
    print("=== send_email() CALLED ===")
    print("To:", to_email)

    try:
        params = {
            "from": "Millrod Swim <info@millrodswim.com>",
            "to": [to_email],
            "bbc": [OWNER_EMAIL],
            "subject": subject,
            "text": body,
        }

        if attachment:
            with open(attachment, "rb") as f:
                pdf_content = base64.b64encode(f.read()).decode("utf-8")

            params["attachments"] = [
                {
                    "filename": "pool_registration.pdf",
                    "content": pdf_content
                }
            ]

        response = resend.Emails.send(params)

        print("SUCCESS!")
        print(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("EMAIL ERROR:", repr(e))



     

def create_registration_pdf(data):

    import uuid
    from xml.sax.saxutils import escape

    filename = f"pool_registration_{uuid.uuid4()}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Swimming Pool Registration",
            styles["Title"]
        )
    )

    content.append(Spacer(1,20))


    for field, value in data.items():

        text = (
            f"<b>{field.replace('_',' ').title()}:</b> "
            f"{escape(str(value))}"
        )

        content.append(
            Paragraph(
                text,
                styles["Normal"]
            )
        )

        content.append(
            Spacer(1,10)
        )


    doc.build(content)

    return filename



@app.route("/register", methods=["POST"])
def register():

    form_data = request.form.to_dict()
    
    first_name = request.form.get("first_name")
    parent_email = request.form.get("parent_email")
    schedule_id = request.form.get("schedule_id")

    pdf_file = create_registration_pdf(form_data)

    registration_email = """
New Swimming Registration

A new registration was submitted.

The complete registration form is attached as a PDF.
"""


    thank_you_email = f"""
Dear Parent/Guardian,

Thank you for registering {first_name} with Millrod Swim!

We have successfully received your registration.

Our team will review your information and contact you soon with the next steps.

Thank you for choosing Millrod Swim!

Millrod Swim Team
"""

    # Send email to owner
    send_email(
        OWNER_EMAIL,
        "New Pool Registration",
        registration_email,
        pdf_file
    )


    # # Send confirmation to parent
    # print("PARENT EMAIL:", parent_email)

    # if parent_email:
    #     send_email(
    #         parent_email,
    #         "Thank you for your registration",
    #         thank_you_email
    #     )


    print("PARENT EMAIL:", parent_email)

    if parent_email:
        print("Sending confirmation email to parent...")

        send_email(
            parent_email,
            "Thank you for your registration",
            thank_you_email
        )

        print("Finished sending confirmation email.")
    else:
        print("No parent email found.")
        
        

    conn = sqlite3.connect("pool.db")
    cursor = conn.cursor()


    # Check if already booked
    cursor.execute(
        """
        SELECT booked 
        FROM schedule
        WHERE id=?
        """,
        (schedule_id,)
    )

    slot = cursor.fetchone()


    if slot and slot[0] == 1:
        conn.close()
        return "This time is already booked. Please choose another time."


    # Mark as booked
    cursor.execute(
        """
        UPDATE schedule
        SET booked = 1
        WHERE id=?
        """,
        (schedule_id,)
    )


    conn.commit()
    conn.close()

    
        

    return "Registration submitted successfully!"






if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
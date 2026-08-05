import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import uuid
from xml.sax.saxutils import escape
import resend
import sqlite3
import traceback
import base64
from datetime import datetime
from flask import Flask, request, render_template, jsonify



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




# ==================================
# ADD DATABASE HERE
# ==================================

DATABASE = "bookings.db"


def init_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (

id INTEGER PRIMARY KEY AUTOINCREMENT,

student_name TEXT,
dob TEXT,
age TEXT,

parent_name TEXT,
email TEXT,
phone TEXT,

emergency_name TEXT,
emergency_phone TEXT,

level TEXT,
experience TEXT,
goal TEXT,

lesson_type TEXT,
number_lessons TEXT,
instructor TEXT,

lesson_date TEXT,
lesson_time TEXT,

medical TEXT,
notes TEXT,

agreement TEXT,

created_at TEXT

)
""")

    conn.commit()

    conn.close()

init_database()


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/test")
def test():
    return "Flask is working!"



@app.route("/bookings")
def bookings():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT lesson_date, lesson_time
        FROM bookings
    """)

    rows = cursor.fetchall()

    conn.close()


    events = []


    for row in rows:

        events.append({

            "title": "Booked - " + row[1],

            "start": row[0],

            "allDay": True

        })


    return jsonify(events)


def send_email(to_email, subject, body, attachment=None):
    print("=== send_email() CALLED ===")
    print("To:", to_email)

    try:
        params = {
            "from": "Millrod Swim <info@millrodswim.com>",
            "to": [to_email],
            # "bcc": [OWNER_EMAIL],
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


    hidden_fields = [
        "schedule_id"
    ]

    for field, value in data.items():

        if field in hidden_fields:
            continue

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


    student_name = form_data.get("student_name")

    parent_email = form_data.get("email")

    lesson_date = form_data.get("lesson_date")

    lesson_time = form_data.get("lesson_time")




    # ==============================
    # CHECK EXISTING BOOKINGS
    # ==============================


    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()



    cursor.execute("""
        SELECT * FROM bookings
        WHERE lesson_date = ?
        AND lesson_time = ?

    """,
    (
        lesson_date,
        lesson_time
    ))



    existing = cursor.fetchone()



    if existing:

        conn.close()

        return jsonify({

            "success": False,

            "message": "This date and time is already booked. Please choose another lesson time."

        })





    # ==============================
    # SAVE BOOKING
    # ==============================


    cursor.execute("""
    INSERT INTO bookings
    (
    student_name,
    dob,
    age,

    parent_name,
    email,
    phone,

    emergency_name,
    emergency_phone,

    level,
    experience,
    goal,

    lesson_type,
    number_lessons,
    instructor,

    lesson_date,
    lesson_time,

    medical,
    notes,

    agreement,

    created_at

    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

    """,
    (

    form_data.get("student_name"),

    form_data.get("dob"),

    form_data.get("age"),


    form_data.get("parent_name"),

    form_data.get("email"),

    form_data.get("phone"),


    form_data.get("emergency_name"),

    form_data.get("emergency_phone"),


    form_data.get("level"),

    form_data.get("experience"),

    form_data.get("goal"),


    form_data.get("lesson_type"),

    form_data.get("number_lessons"),

    form_data.get("instructor"),


    lesson_date,

    lesson_time,


    form_data.get("medical"),

    form_data.get("notes"),


    form_data.get("agreement"),


    datetime.now().isoformat()

    ))



    conn.commit()

    conn.close()





    # ==============================
    # CREATE PDF
    # ==============================


    pdf_file = create_registration_pdf(form_data)





    # ==============================
    # SEND OWNER EMAIL
    # ==============================


    send_email(

        OWNER_EMAIL,

        "New Millrod Swim Registration",

        "A new swimming lesson registration was received.",

        pdf_file

    )





    # ==============================
    # SEND PARENT CONFIRMATION
    # ==============================


    if parent_email:


        send_email(

            parent_email,

            "Millrod Swim Registration Confirmation",

            f"""
Dear Parent/Guardian,

Thank you for registering {student_name} with Millrod Swim Academy.

Your requested lesson:

Date: {lesson_date}
Time: {lesson_time}

We will contact you soon with confirmation.

Thank you,

Millrod Swim Academy
"""

        )




    return jsonify({

    "success": True,

    "message": "Registration submitted successfully!"

})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
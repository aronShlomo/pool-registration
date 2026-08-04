from flask import Flask, request, render_template
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape
from dotenv import load_dotenv

import os
import uuid
import sqlite3
import base64
import resend


app = Flask(__name__)


load_dotenv()


OWNER_EMAIL = os.getenv("POOL_EMAIL")
resend.api_key = os.getenv("RESEND_API_KEY")


print("POOL_EMAIL:", OWNER_EMAIL)
print("RESEND_API_KEY exists:", os.getenv("RESEND_API_KEY") is not None)



# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

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



# ---------------- CALENDAR DATA ----------------

@app.route("/schedule")
def schedule():

    conn = sqlite3.connect("pool.db")
    cursor = conn.cursor()


    cursor.execute("""
        SELECT id,
               lesson_date,
               lesson_time,
               class_name,
               booked
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




# ---------------- SEND EMAIL ----------------

def send_email(to_email, subject, body, attachment=None):

    print("=== send_email() CALLED ===")
    print("To:", to_email)


    try:

        params = {

            "from": "Millrod Swim <info@millrodswim.com>",

            "to": [to_email],

            "bcc": [OWNER_EMAIL],

            "subject": subject,

            "text": body

        }


        if attachment:

            with open(attachment, "rb") as f:

                pdf_content = base64.b64encode(
                    f.read()
                ).decode("utf-8")


            params["attachments"] = [

                {
                    "filename": "pool_registration.pdf",
                    "content": pdf_content
                }

            ]


        response = resend.Emails.send(params)


        print("EMAIL SENT")
        print(response)


    except Exception as e:

        print("EMAIL ERROR:", repr(e))





# ---------------- CREATE PDF ----------------

def create_registration_pdf(data):


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


    content.append(
        Spacer(1,20)
    )


    for field,value in data.items():

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





# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():


    form_data = request.form.to_dict()


    first_name = request.form.get("first_name")

    parent_email = request.form.get("parent_email")

    schedule_id = request.form.get("schedule_id")

    
    schedule_id = request.form.get("schedule_id")

    print("========== SCHEDULE DEBUG ==========")
    print("schedule_id received:", schedule_id)
    print("ALL FORM DATA:", request.form)
    print("====================================")


    print("SELECTED SCHEDULE ID:", schedule_id)



    conn = sqlite3.connect("pool.db")

    cursor = conn.cursor()



    # Check if slot already booked

    cursor.execute("""
        SELECT booked
        FROM schedule
        WHERE id=?
    """,
    (schedule_id,))


    slot = cursor.fetchone()



    if not slot:

        conn.close()

        return "Invalid schedule selected"



    if slot[0] == 1:

        conn.close()

        return "This lesson time is already booked. Please choose another time."





    # Get selected lesson information

    cursor.execute("""
        SELECT lesson_date,
               lesson_time,
               class_name
        FROM schedule
        WHERE id=?
    """,
    (schedule_id,))


    selected_schedule = cursor.fetchone()



    if selected_schedule:


        form_data["Swimming Date"] = selected_schedule[0]

        form_data["Swimming Time"] = selected_schedule[1]

        form_data["Swimming Class"] = selected_schedule[2]




    # Create PDF

    pdf_file = create_registration_pdf(form_data)





    owner_message = """

New Swimming Registration


A new registration was submitted.

The registration PDF is attached.

"""



    parent_message = f"""

Dear Parent/Guardian,


Thank you for registering {first_name} with Millrod Swim!


We received your registration.

Our team will review your information and contact you soon.


Thank you!


Millrod Swim Team

"""




    # Send owner email

    send_email(

        OWNER_EMAIL,

        "New Pool Registration",

        owner_message,

        pdf_file

    )




    # Send parent email

    if parent_email:


        send_email(

            parent_email,

            "Thank you for your registration",

            parent_message

        )





    # Mark schedule as booked

    cursor.execute("""
        UPDATE schedule
        SET booked = 1
        WHERE id=?
    """,
    (schedule_id,))



    conn.commit()

    conn.close()



    return "Registration submitted successfully!"





if __name__ == "__main__":


    port = int(
        os.environ.get("PORT",5000)
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
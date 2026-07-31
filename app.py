from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

from dotenv import load_dotenv
import os

load_dotenv()

OWNER_EMAIL = os.getenv("POOL_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


@app.route("/")
def home():
    return render_template("index.html")


def send_email(to_email, subject, body, attachment=None):

    msg = EmailMessage()

    msg["From"] = OWNER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content(body)


    if attachment:

        with open(attachment, "rb") as file:

            file_data = file.read()


        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="pdf",
            filename="Swimming_Registration.pdf"
        )


    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            OWNER_EMAIL,
            EMAIL_PASSWORD
        )

        server.send_message(msg)

def create_registration_pdf(data):

    filename = "pool_registration.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "Swimming Pool Registration",
        styles["Title"]
    )

    content.append(title)
    content.append(Spacer(1, 20))


    for field, value in data.items():

        text = f"<b>{field.replace('_',' ').title()}:</b> {value}"

        content.append(
            Paragraph(
                text,
                styles["Normal"]
            )
        )

        content.append(
            Spacer(1, 10)
        )


    doc.build(content)

    return filename        


        
        
@app.route("/register", methods=["POST"])
def register():

    # Get ALL form information

    form_data = request.form.to_dict()


    # Create PDF

    pdf_file = create_registration_pdf(form_data)


    # Email to owner

    registration_email = """

New Swimming Registration

A new registration was submitted.

The complete registration form is attached as a PDF.

"""


    send_email(
        OWNER_EMAIL,
        "New Pool Registration",
        registration_email,
        pdf_file
    )


    # Get parent email

    parent_email = request.form.get("parent_email")


    # Confirmation email

    thank_you_email = """

Thank you for your registration!

We received your swimming registration form.

Our team will review your information and get back to you as soon as possible.

Thank you.

Swimming Pool Team

"""


    send_email(
        parent_email,
        "Thank you for your registration",
        thank_you_email
    )


    return """
    Registration submitted successfully!
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import uuid
from xml.sax.saxutils import escape
import resend



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
    return render_template("index.html")

import traceback


def send_email(to_email, subject, body, attachment=None):
    try:
        print("=== SENDING EMAIL ===")
        print("To:", to_email)

        params = {
            "from": "Millrod Swim <onboarding@resend.dev>",  # or your verified domain
            "to": [to_email],
            "subject": subject,
            "text": body,
        }

        response = resend.Emails.send(params)

        print("RESEND RESPONSE:", response)

    except Exception as e:
        print("EMAIL ERROR:", repr(e))

# def create_registration_pdf(data):

#     # filename = "pool_registration.pdf"
#     filename = f"pool_registration_{uuid.uuid4()}.pdf"

#     doc = SimpleDocTemplate(
#         filename,
#         pagesize=letter
#     )

#     styles = getSampleStyleSheet()

#     content = []

#     title = Paragraph(
#         "Swimming Pool Registration",
#         styles["Title"]
#     )

#     content.append(title)
#     content.append(Spacer(1, 20))


#     for field, value in data.items():

#         # text = f"<b>{field.replace('_',' ').title()}:</b> {value}"
#         text = f"<b>{field.replace('_',' ').title()}:</b> {escape(str(value))}"

#         content.append(
#             Paragraph(
#                 text,
#                 styles["Normal"]
#             )
#         )

#         content.append(
#             Spacer(1, 10)
#         )


#     doc.build(content)

#     return filename        

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


# @app.route("/register", methods=["POST"])
# def register():

#     form_data = request.form.to_dict()

#     pdf_file = create_registration_pdf(form_data)

#     try:
#         send_email(
#             OWNER_EMAIL,
#             "New Pool Registration",
#             "A new registration was submitted.",
#             pdf_file
#         )

#     except Exception as e:
#         print("Email failed:", e)


#     return "Registration submitted successfully!"
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

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
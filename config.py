import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =====================
    # Flask
    # =====================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-in-production"
    )


    # =====================
    # Database
    # =====================

    DATABASE = os.getenv(
        "DATABASE",
        "bookings.db"
    )


    # =====================
    # Resend Email
    # =====================

    RESEND_API_KEY = os.getenv(
        "RESEND_API_KEY"
    )

    # Email receiving booking notifications
    OWNER_EMAIL = os.getenv(
        "OWNER_EMAIL",
        "themillrodswim@gmail.com"
    )

    # Sender email (must be verified in Resend)
    EMAIL_FROM = os.getenv(
        "EMAIL_FROM",
        "Millrod Swim Academy <info@millrodswim.com>"
    )


    # =====================
    # Stripe
    # =====================

    STRIPE_SECRET_KEY = os.getenv(
        "STRIPE_SECRET_KEY"
    )

    STRIPE_PUBLISHABLE_KEY = os.getenv(
        "STRIPE_PUBLISHABLE_KEY"
    )

    STRIPE_WEBHOOK_SECRET = os.getenv(
        "STRIPE_WEBHOOK_SECRET"
    )


    # =====================
    # Admin Login
    # =====================

    ADMIN_USERNAME = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "change-me"
    )


    # =====================
    # Stripe Settings
    # =====================

    CURRENCY = "usd"

    TEST_MODE = os.getenv(
        "TEST_MODE",
        "True"
    ).lower() == "true"



    # =====================
    # Website URL
    # =====================

    DOMAIN = os.getenv(
        "DOMAIN",
        "http://localhost:5000"
    )



    # =====================
    # Lesson Prices
    # Stripe uses cents
    # Example:
    # 8000 = $80.00
    # =====================

    LESSON_PRICES = {

        "Private Lesson": {

            "Single Lesson": 8000,

            "4 Lessons Package": 30000,

            "8 Lessons Package": 56000,

            "Monthly Program": 100000
        },


        "Semi-Private Lesson": {

            "Single Lesson": 12000,

            "4 Lessons Package": 45000,

            "8 Lessons Package": 85000,

            "Monthly Program": 150000
        },


        "Group Lesson": {

            "Single Lesson": 6000,

            "4 Lessons Package": 22000,

            "8 Lessons Package": 40000,

            "Monthly Program": 70000
        }

    }



    # =====================
    # Company Information
    # =====================

    COMPANY_NAME = "Millrod Swim Academy"

    COMPANY_EMAIL = "info@millrodswim.com"

    COMPANY_PHONE = "(555) 555-5555"

import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # Flask
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-in-production"
    )


    # Database
    DATABASE = os.getenv(
        "DATABASE",
        "bookings.db"
    )


    # Resend
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    OWNER_EMAIL = os.getenv("POOL_EMAIL")


    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


    # Website URL
    DOMAIN = os.getenv(
        "DOMAIN",
        "http://localhost:5000"
    )


    # Pricing (in cents)
    LESSON_PRICES = {

        "Private Lesson": {
            "Single Lesson": 6000,
            "4 Lessons Package": 22000,
            "8 Lessons Package": 42000,
            "Monthly Program": 50000,
        },

        "Semi-Private Lesson": {
            "Single Lesson": 4500,
            "4 Lessons Package": 16000,
            "8 Lessons Package": 30000,
            "Monthly Program": 36000,
        },

        "Group Lesson": {
            "Single Lesson": 3000,
            "4 Lessons Package": 11000,
            "8 Lessons Package": 20000,
            "Monthly Program": 24000,
        },
    }


    COMPANY_NAME = "Millrod Swim Academy"

    COMPANY_EMAIL = "info@millrodswim.com"

    COMPANY_PHONE = "(555) 555-5555"

    CURRENCY = "usd"
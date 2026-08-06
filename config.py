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


    COMPANY_NAME = "Millrod Swim Academy"

    COMPANY_EMAIL = "info@millrodswim.com"

    COMPANY_PHONE = "(555) 555-5555"

    CURRENCY = "usd"
import os
import smtplib

from email.message import EmailMessage


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USER = os.getenv(
    "SMTP_USER",
    ""
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
)



def send_password_reset_email(
    email: str,
    reset_link: str
):

    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError(
            "Email SMTP credentials are not configured"
        )


    message = EmailMessage()

    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = "Password Reset Request"


    message.set_content(
        f"""
Hello,

You requested a password reset.

Click the link below to reset your password:

{reset_link}

This link will expire after 30 minutes.

If you did not request this, please ignore this email.

Regards,
Your Exam Preparation Platform
"""
    )


    try:

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                SMTP_USER,
                SMTP_PASSWORD
            )

            server.send_message(
                message
            )


        return True


    except Exception as error:

        raise RuntimeError(
            f"Email sending failed: {error}"
        )
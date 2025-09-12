import json
import smtplib
from email.message import EmailMessage

# Load JSON data
with open("invitees.json", "r") as f:
    invitees = json.load(f)

# Email credentials (replace with your actual credentials)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "jonathan.moore6247@gmail.com"
SENDER_PASSWORD = "oxpmyqitfbeeonki"  # Use an App Password if using Gmail

def send_email(to_address, message_body):
    msg = EmailMessage()
    msg["Subject"] = "Andrea & Jonathan - Wedding Invitation 2026"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_address
    msg.set_content(message_body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        print(f"Email sent to {to_address}")

# Loop through invitees and send emails
for person in invitees:
    email = person.get("Email Address")
    message = person.get("Message")

    if email and message:
        send_email(email, message)

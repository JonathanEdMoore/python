import json
import smtplib
from email.message import EmailMessage

# Load JSON data
with open("weddinginvite.json", "r") as f:
    invitees = json.load(f)

# Email credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "jonathan.moore6247@gmail.com"
SENDER_PASSWORD = "oxpmyqitfbeeonki"  # App Password for Gmail

def send_email(to_address, message_text, message_html):
    msg = EmailMessage()
    msg["Subject"] = "REMINDER: Jonathan and Andrea Wedding | RSVP by Oct 31, 2025"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_address

    # Plain-text version (for fallback)
    msg.set_content(message_text)

    # HTML version (main)
    msg.add_alternative(message_html, subtype="html")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        print(f"Email sent to {to_address}")

# Loop through invitees and send emails
for person in invitees:
    email = person.get("Email Address")
    name = person.get("First Name")
    full_name = person.get("Full Name")
    rsvp_status = person.get("RSVP status")

    if rsvp_status == "No response" and email:
        # Plain text fallback
        message_text = f"""Hello, {name}!
This is a reminder to update your response (confirm or decline) to our wedding no later than October 31, 2025. Your spot will be reserved only if you complete the RSVP. If we don’t receive your response, we’ll assume you won’t be able to join us.

To update your response:
• Open our invitation here: https://bodaandreayjonathan.swanmoments.net/en/
• Scroll to the end of the invitation and locate the RSVP link.
• Enter your name exactly as it appears on the invitation: {full_name}.
• If you don’t see your name or have any issues, please contact us.

Website: On the invitation, you’ll find a link to the website with details about the updated itinerary, travel, FAQ, and more. If accessing from your phone, tap the ☰ icon in the top right corner to see the full menu.

Thank you for confirming and helping us plan this very special day!
"""

        # HTML version (with formatting and bold full name)
        message_html = f"""\
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
    <p>Hello, {name}!</p>
    <p>This is a reminder to update your response (confirm or decline) to our wedding no later than <b>October 31, 2025</b>. Your spot will be reserved only if you complete the RSVP. If we don’t receive your response, we’ll assume you won’t be able to join us.</p>

    <p><b>To update your response:</b></p>
    <ul>
      <li>Open our invitation here: <a href="https://bodaandreayjonathan.swanmoments.net/en/">https://bodaandreayjonathan.swanmoments.net/en/</a></li>
      <li>Scroll to the end of the invitation and locate the RSVP link.</li>
      <li>Enter your name exactly as it appears on the invitation: <b>{full_name}</b>.</li>
      <li>If you don’t see your name or have any issues, please contact us.</li>
    </ul>

    <p>Website: On the invitation, you’ll find a link to the website with details about the updated itinerary, travel, FAQ, and more. If accessing from your phone, tap the ☰ icon in the top right corner to see the full menu.</p>

    <p>Thank you for confirming and helping us plan this very special day!</p>
  </body>
</html>
"""

        send_email(email, message_text, message_html)

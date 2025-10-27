import smtplib
from email.mime.text import MIMEText
import os

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = to

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            server.send_message(msg)
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
import os
import requests

def send_email(to, subject, body):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": os.getenv("BREVO_API_KEY"),
        "Content-Type": "application/json"
    }
    data = {
        "sender": {"name": "Fraud Detection", "email": os.getenv("EMAIL_USER")},
        "to": [{"email": to}],
        "subject": subject,
        "textContent": body
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Failed to send email via API: {e}")
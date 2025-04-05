import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

REFERRAL_LOG = "referrals.json"

# Update these for your environment
EMAIL_SENDER = "your-email@example.com"
EMAIL_RECEIVER = "doctor@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
EMAIL_PASSWORD = "your-password"


def log_referral(session_id, symptoms, drug, confidence):
    os.makedirs(os.path.dirname(REFERRAL_LOG), exist_ok=True)
    entry = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "symptoms": symptoms,
        "recommended_drug": drug,
        "confidence": confidence
    }

    if os.path.exists(REFERRAL_LOG):
        with open(REFERRAL_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(REFERRAL_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_referral_email(session_id, drug, symptoms):
    try:
        subject = f"🚨 MYD Referral Triggered – Session {session_id}"
        body = f"A patient has been flagged for urgent attention.\n\nSession ID: {session_id}\nRecommended Drug: {drug}\nSymptoms: {symptoms}"

        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📩 Referral email sent.")
    except Exception as e:
        print("❌ Failed to send referral email:", str(e))

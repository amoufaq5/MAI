# referral_logger.py
import json
import os
from datetime import datetime

PROFILE_PATH = "user_profiles.json"
REFERRAL_PATH = "referrals.json"
OUTBREAK_PATH = "outbreak_log.json"


def save_user_profile(username, symptoms, predictions, asmethod):
    entry = {
        "user": username,
        "timestamp": datetime.now().isoformat(),
        "symptoms": symptoms,
        "asmethod": asmethod,
        "predictions": predictions
    }
    _append_json(PROFILE_PATH, entry)


def log_referral(username, disease, symptoms, drug, asmethod):
    entry = {
        "user": username,
        "timestamp": datetime.now().isoformat(),
        "disease": disease,
        "drug": drug,
        "reason": symptoms,
        "asmethod": asmethod
    }
    _append_json(REFERRAL_PATH, entry)


def log_outbreak(disease):
    date = datetime.now().strftime("%Y-%m-%d")
    entry = {"date": date, "disease": disease}
    _append_json(OUTBREAK_PATH, entry)


def _append_json(filepath, data):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
    else:
        existing = []

    existing.append(data)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

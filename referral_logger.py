import json
import os
from datetime import datetime

REFERRAL_FILE = "referrals.json"
OUTBREAK_FILE = "outbreak_log.json"
PROFILE_FILE = "user_profiles.json"

def log_referral(username, disease, symptoms, drug):
    entry = {
        "username": username,
        "datetime": str(datetime.now()),
        "disease": disease,
        "symptoms": symptoms,
        "suggested_drug": drug,
        "reason": "Requires prescription. Referred to doctor."
    }
    _append_json(REFERRAL_FILE, entry)

def log_outbreak(disease):
    today = datetime.today().strftime('%Y-%m-%d')
    entry = {"date": today, "disease": disease}
    _append_json(OUTBREAK_FILE, entry)

def save_user_profile(username, symptoms, disease):
    profile = {
        "username": username,
        "datetime": str(datetime.now()),
        "symptoms": symptoms,
        "diagnosis": disease
    }
    _append_json(PROFILE_FILE, profile)

def _append_json(file, data):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump([], f)
    with open(file, "r+") as f:
        logs = json.load(f)
        logs.append(data)
        f.seek(0)
        json.dump(logs, f, indent=2)

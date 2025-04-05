import os
import json
from datetime import datetime

PROFILE_DIR = "user_profiles"
os.makedirs(PROFILE_DIR, exist_ok=True)

def save_user_profile(session_id, answers, lang):
    profile = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "language": lang,
        "profile": {
            "age_appearance": answers[0],
            "for_whom": answers[1],

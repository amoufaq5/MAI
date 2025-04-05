import os
import json
from datetime import datetime

LOG_DIR = 'chat_logs'
os.makedirs(LOG_DIR, exist_ok=True)

def start_new_session():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"session_{timestamp}"
    filepath = os.path.join(LOG_DIR, f"{session_id}.json")
    with open(filepath, 'w') as f:
        json.dump({"session_id": session_id, "timestamp": timestamp, "messages": []}, f, indent=2)
    return session_id, filepath

def log_message(filepath, role, message):
    with open(filepath, 'r') as f:
        data = json.load(f)

    data["messages"].append({
        "role": role,  # user or bot
        "text": message,
        "time": datetime.now().isoformat()
    })

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def log_final_recommendation(filepath, drug, confidence, side_effects):
    with open(filepath, 'r') as f:
        data = json.load(f)

    data["recommendation"] = {
        "drug": drug,
        "confidence": round(confidence, 2),
        "side_effects": side_effects
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

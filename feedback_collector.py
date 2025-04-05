import os
import json

FEEDBACK_FILE = "feedback.json"

def store_feedback(session_id, input_text, predicted_drug, correct_drug, feedback_type):
    entry = {
        "session_id": session_id,
        "input": input_text,
        "predicted_drug": predicted_drug,
        "correct_drug": correct_drug,
        "feedback": feedback_type  # 'positive' or 'correction'
    }

    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

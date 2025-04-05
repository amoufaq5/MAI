import json
import re

with open("clarification_data.json", "r") as f:
    CLARIFICATION_DATA = json.load(f)

def detect_symptoms_for_clarification(text):
    found = []
    for keyword in CLARIFICATION_DATA:
        if re.search(rf"\b{keyword}\b", text.lower()):
            found.append(keyword)
    return found

def get_clarification_questions(symptom):
    return CLARIFICATION_DATA.get(symptom, [])

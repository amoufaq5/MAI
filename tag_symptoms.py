# tag_symptoms.py
import spacy
import json
import os

# Load a pre-trained medical-aware SpaCy model or fallback to en_core_web_sm
try:
    nlp = spacy.load("en_core_sci_sm")  # For SciSpaCy users
except:
    nlp = spacy.load("en_core_web_sm")

def extract_medical_ents(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_.lower() in {"disease", "symptom", "drug", "medication", "condition"}]

def tag_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        for entry in data:
            cleaned = entry.get("cleaned", entry.get("content", ""))
            entry["tags"] = extract_medical_ents(cleaned)
    else:
        cleaned = data.get("cleaned", data.get("content", ""))
        data["tags"] = extract_medical_ents(cleaned)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    sample = "data/webmd/raw/Flu_Symptoms_and_Treatment_cleaned.json"
    output = sample.replace(".json", "_tagged.json")
    tag_file(sample, output)
    print("✅ Tagged and saved:", output)

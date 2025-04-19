# synthetic_data_generator.py
import json
import random
import os

symptoms = [
    "fever", "headache", "fatigue", "cough", "sore throat", "nausea", "vomiting",
    "shortness of breath", "rash", "chest pain", "diarrhea", "dizziness"
]

conditions = [
    "common cold", "influenza", "migraine", "food poisoning", "bronchitis",
    "covid-19", "allergic reaction", "pneumonia", "gastritis", "asthma"
]

recommendations = [
    "Take OTC paracetamol for fever and rest well.",
    "Use ibuprofen for pain relief and drink plenty of fluids.",
    "If symptoms persist for more than 3 days, consult a doctor.",
    "Avoid crowded places and wear a mask.",
    "Refer to the emergency department for chest pain."
]

def generate_case():
    selected_symptoms = random.sample(symptoms, k=random.randint(2, 4))
    diagnosis = random.choice(conditions)
    advice = random.choice(recommendations)

    return {
        "input": f"Patient reports {', '.join(selected_symptoms)}.",
        "output": f"Likely diagnosis: {diagnosis}. Recommendation: {advice}"
    }

def generate_dataset(n=1000, output_path="data/synthetic/train_synthetic.jsonl"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for _ in range(n):
            case = generate_case()
            f.write(json.dumps(case) + "\n")
    print(f"✅ Generated {n} synthetic medical cases at {output_path}")

if __name__ == '__main__':
    generate_dataset()

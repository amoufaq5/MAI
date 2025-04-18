# chatbot.py
import json
from predictor import predict_top_diseases
from referral_logger import save_user_profile, log_referral
from symptom_clarifier import detect_symptoms_for_clarification, get_clarification_questions
import pandas as pd

with open("asmethod_data.json") as f:
    ASMETHOD_QUESTIONS = json.load(f)

drug_df = pd.read_csv("data.csv")

class ChatBot:
    def __init__(self, username="guest"):
        self.username = username
        self.reset()

    def reset(self):
        self.state = "ASMETHOD"
        self.asmethod_keys = list(ASMETHOD_QUESTIONS.keys())
        self.current_ask_index = 0
        self.asmethod_answers = {}
        self.symptoms = ""
        self.pending_symptoms = []
        self.pending_questions = []
        self.clarified = {}
        self.clarification_mode = False

    def handle_message(self, msg):
        if msg.lower() == "start":
            self.reset()
            return ASMETHOD_QUESTIONS[self.asmethod_keys[self.current_ask_index]]

        if self.state == "ASMETHOD":
            key = self.asmethod_keys[self.current_ask_index]
            self.asmethod_answers[key] = msg
            self.current_ask_index += 1

            if self.current_ask_index < len(self.asmethod_keys):
                return ASMETHOD_QUESTIONS[self.asmethod_keys[self.current_ask_index]]
            else:
                self.symptoms = self.asmethod_answers.get("O", "")
                self.pending_symptoms = detect_symptoms_for_clarification(self.symptoms)
                if self.pending_symptoms:
                    self.state = "CLARIFICATION"
                    return self._ask_next_clarification()
                else:
                    return self._final_diagnosis()

        if self.state == "CLARIFICATION":
            last_symptom = self.pending_symptoms[0]
            self.clarified.setdefault(last_symptom, []).append(msg)

            if self.pending_questions:
                return self._ask_next_clarification()
            else:
                self.pending_symptoms.pop(0)
                if self.pending_symptoms:
                    return self._ask_next_clarification()
                else:
                    return self._final_diagnosis()

    def _ask_next_clarification(self):
        symptom = self.pending_symptoms[0]
        if not self.pending_questions:
            self.pending_questions = get_clarification_questions(symptom)
        return self.pending_questions.pop(0)

    def _final_diagnosis(self):
        full_input = self.symptoms + " " + " ".join([" ".join(v) for v in self.clarified.values()])
        predictions = predict_top_diseases(full_input)

        if not predictions:
            return "❌ I couldn't find a confident match. Please see a doctor."

        disease_responses = []
        for disease, confidence in predictions:
            drug, dtype = self._find_drug(disease)
            entry = f"- {disease} ({confidence:.1f}%)"
            if dtype == "OTC":
                entry += f"\n  💊 Recommended OTC: {drug}"
            elif dtype == "RX":
                log_referral(self.username, disease, full_input, drug, self.asmethod_answers)
                entry += f"\n  📩 Referred to doctor for: {drug}"
            disease_responses.append(entry)

        save_user_profile(self.username, full_input, predictions, self.asmethod_answers)

        summary = "\n\n🧾 Clarification Summary:\n" + json.dumps(self.clarified, indent=2)
        return "🧠 Likely conditions:\n" + "\n\n".join(disease_responses) + summary

    def _find_drug(self, disease):
        rows = drug_df[drug_df["disease"].str.lower() == disease.lower()]
        if not rows.empty:
            otc = rows[rows["drug_type"].str.upper() == "OTC"]
            if not otc.empty:
                return otc.iloc[0]["drug name"], "OTC"
            else:
                return rows.iloc[0]["drug name"], "RX"
        return None, None

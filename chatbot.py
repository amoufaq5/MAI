from symptom_clarifier import detect_symptoms_for_clarification, get_clarification_questions
from disease_model import predict_disease
from referral_logger import log_referral, log_outbreak, save_user_profile
import pandas as pd

drug_df = pd.read_csv("data.csv")

class ChatBot:
    def __init__(self, username="guest"):
        self.username = username
        self.reset()

    def reset(self):
        self.symptoms = ""
        self.disease = ""
        self.collected = []
        self.current_index = 0
        self.pending_symptoms = []
        self.pending_questions = []
        self.clarification_mode = False
        self.clarified = {}

    def handle_message(self, msg):
        if msg.lower() == "start":
            self.reset()
            return "🩺 Please describe your symptoms."

        if not self.symptoms:
            self.symptoms = msg
            self.pending_symptoms = detect_symptoms_for_clarification(msg)
            if self.pending_symptoms:
                self.clarification_mode = True
                return self._ask_next_clarification()
            else:
                return self._final_diagnosis()

        if self.clarification_mode:
            last_symptom = self.pending_symptoms[0]
            self.clarified.setdefault(last_symptom, []).append(msg)

            if self.pending_questions:
                return self._ask_next_clarification()
            else:
                self.pending_symptoms.pop(0)
                if self.pending_symptoms:
                    return self._ask_next_clarification()
                else:
                    self.clarification_mode = False
                    return self._final_diagnosis()

    def _ask_next_clarification(self):
        symptom = self.pending_symptoms[0]
        if not self.pending_questions:
            self.pending_questions = get_clarification_questions(symptom)
        return self.pending_questions.pop(0)

    def _final_diagnosis(self):
        enriched = self.symptoms
        for vals in self.clarified.values():
            enriched += " " + " ".join(vals)

        disease, confidence = predict_disease(enriched)
        drug, dtype = self._find_drug(disease)

        save_user_profile(self.username, enriched, disease)
        log_outbreak(disease)

        if dtype == "OTC":
            return f"🧠 Likely: {disease} ({confidence}%)\n💊 OTC Suggestion: {drug}"
        elif dtype == "RX":
            log_referral(self.username, disease, enriched, drug)
            return f"🧠 Likely: {disease} ({confidence}%)\n⚠️ Drug requires a prescription: {drug}\n📩 Referral sent to your doctor."
        else:
            return f"🧠 Likely: {disease} ({confidence}%)\n⚠️ No drug found."

    def _find_drug(self, disease):
        rows = drug_df[drug_df["disease"].str.lower() == disease.lower()]
        if not rows.empty:
            otc = rows[rows["drug_type"].str.upper() == "OTC"]
            if not otc.empty:
                return otc.iloc[0]["drug name"], "OTC"
            else:
                return rows.iloc[0]["drug name"], "RX"
        return None, None

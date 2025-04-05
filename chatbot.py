from disease_model import predict_disease
from referral_logger import log_referral, log_outbreak, save_user_profile
import pandas as pd

class ChatBot:
    def __init__(self, username="guest"):
        self.username = username
        self.questions = [
            "1. Please describe your age and appearance.",
            "2. Is this for you or someone else?",
            "3. Are you taking any medication?",
            "4. Any extra medicines or supplements?",
            "5. How long have you had the symptoms?",
            "6. Any relevant medical history?",
            "7. What symptoms are you experiencing?",
            "8. Are there any danger symptoms?"
        ]
        self.index = 0
        self.responses = []
        self.finished = False
        self.df = pd.read_csv("data.csv")

    def reset(self):
        self.index = 0
        self.responses = []
        self.finished = False

    def find_drug(self, disease):
        match = self.df[self.df["disease"].str.lower() == disease.lower()]
        if not match.empty:
            otc = match[match["drug_type"].str.upper() == "OTC"]
            if not otc.empty:
                return otc.iloc[0]["drug name"], "OTC"
            else:
                return match.iloc[0]["drug name"], "RX"
        return None, None

    def handle_message(self, message):
        if message.lower() == "start":
            self.reset()
            return self.questions[self.index]

        if self.finished:
            return "Type 'start' to begin a new diagnosis."

        self.responses.append(message)
        self.index += 1

        if self.index < len(self.questions):
            return self.questions[self.index]
        else:
            full_input = " ".join(self.responses)
            disease, confidence = predict_disease(full_input)
            drug, dtype = self.find_drug(disease)

            log_outbreak(disease)
            save_user_profile(self.username, full_input, disease)

            self.finished = True

            if dtype == "OTC":
                return (
                    f"🧠 Most likely condition: {disease} ({confidence}%)\n"
                    f"💊 You can take: **{drug}** (Over-the-counter)"
                )
            elif dtype == "RX":
                log_referral(self.username, disease, full_input, drug)
                return (
                    f"🧠 Most likely condition: {disease} ({confidence}%)\n"
                    f"⚠️ This drug requires a prescription: **{drug}**\n"
                    f"📩 Your case has been referred to a doctor with your notes."
                )
            else:
                return (
                    f"🧠 Most likely condition: {disease} ({confidence}%)\n"
                    f"⚠️ No suitable drug was found in our records. Please consult a healthcare provider."
                )

from session_logger import start_new_session, log_message, log_final_recommendation
from model import predict_drug
from response_templates import make_human_response
from langdetect import detect
from user_profile import save_user_profile
from feedback_collector import store_feedback
from fhir_exporter import generate_fhir_bundle
import json
import os

class ChatBot:
    def __init__(self, model, vectorizer, encoder, df):
        self.model = model
        self.vectorizer = vectorizer
        self.encoder = encoder
        self.df = df

        self.questions_en = [
            "Please provide your age and appearance.",
            "Is it you or someone else experiencing symptoms?",
            "Any current medications?",
            "Any extra medicines or supplements?",
            "How long has this been going on?",
            "Any relevant medical history?",
            "What symptoms are you experiencing?",
            "Are there any danger symptoms?"
        ]

        self.questions_ar = [
            "يرجى وصف عمرك ومظهرك.",
            "هل الأعراض لك أم لشخص آخر؟",
            "هل تأخذ أي أدوية حالياً؟",
            "هل تستخدم أدوية إضافية أو مكملات؟",
            "منذ متى بدأت هذه الأعراض؟",
            "هل لديك تاريخ مرضي مهم؟",
            "ما الأعراض التي تعاني منها؟",
            "هل هناك أعراض خطيرة؟"
        ]

        self.questions = self.questions_en  # default
        self.current_index = 0
        self.collected = []
        self.finished = False
        self.feedback_stage = False
        self.waiting_for_feedback = False
        self.corrected_drug = None
        self.lang = "en"
        self.session_id, self.log_file = start_new_session()
        self.last_prediction = None
        self.last_input_text = ""

    def handle_message(self, message):
        log_message(self.log_file, "user", message)

        # Detect language
        try:
            self.lang = detect(message)
        except:
            self.lang = "en"

        # Use proper language set
        self.questions = self.questions_ar if self.lang == "ar" else self.questions_en

        # Reset if conversation is finished
        if self.finished and not self.waiting_for_feedback:
            self.reset()
            response = "ابدأ من جديد بكتابة 'start'" if self.lang == "ar" else "Type 'start' to begin a new diagnosis."
            log_message(self.log_file, "bot", response)
            return response

        # Handle restart
        if message.lower() == 'start':
            self.reset()
            self.questions = self.questions_ar if self.lang == "ar" else self.questions_en
            response = self.questions[0]
            log_message(self.log_file, "bot", response)
            return response

        # Handle feedback response
        if self.waiting_for_feedback:
            if message.strip().lower() in ["yes", "نعم"]:
                store_feedback(self.session_id, self.last_input_text, self.last_prediction, self.last_prediction, "positive")
                response = "Thank you for confirming!" if self.lang == "en" else "شكراً لتأكيدك!"
                self.waiting_for_feedback = False
                log_message(self.log_file, "bot", response)
                return response
            else:
                self.feedback_stage = True
                self.waiting_for_feedback = False
                response = "What drug did you end up using instead?" if self.lang == "en" else "ما الدواء الذي استخدمته بدلاً من ذلك؟"
                log_message(self.log_file, "bot", response)
                return response

        if self.feedback_stage:
            self.corrected_drug = message.strip()
            store_feedback(self.session_id, self.last_input_text, self.last_prediction, self.corrected_drug, "correction")
            self.feedback_stage = False
            response = "Thanks! I've logged your correction to improve future results." if self.lang == "en" else "شكراً! تم تسجيل المعلومة لتحسين النتائج مستقبلاً."
            log_message(self.log_file, "bot", response)
            return response

        # Normal diagnostic flow
        if self.current_index < len(self.questions):
            self.collected.append(message)
            self.current_index += 1

        if self.current_index < len(self.questions):
            response = self.questions[self.current_index]
            log_message(self.log_file, "bot", response)
            return response
        else:
            # Process recommendation
            full_input = " ".join(self.collected)
            drug, confidence, side_effects = predict_drug(
                full_input, self.model, self.vectorizer, self.encoder, self.df
            )
            self.finished = True
            self.waiting_for_feedback = True
            self.last_prediction = drug
            self.last_input_text = full_input

            # Save user profile and logs
            save_user_profile(self.session_id, self.collected, self.lang)
            log_final_recommendation(self.log_file, drug, confidence, side_effects)

            # Generate FHIR export bundle
            bundle = generate_fhir_bundle(
                self.session_id,
                {
                    "age_appearance": self.collected[0],
                    "for_whom": self.collected[1],
                    "medications": self.collected[2],
                    "extras": self.collected[3],
                    "duration": self.collected[4],
                    "history": self.collected[5],
                    "symptoms": self.collected[6],
                    "danger_signs": self.collected[7]
                },
                {
                    "drug": drug,
                    "confidence": confidence,
                    "side_effects": side_effects
                },
                self.lang
            )

            os.makedirs("ehr_exports", exist_ok=True)
            with open(f"ehr_exports/fhir_bundle_{self.session_id}.json", "w", encoding="utf-8") as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)

            response = make_human_response(drug, confidence, side_effects, lang=self.lang)
            response += "\n\nDid this help you? (yes/no)" if self.lang == "en" else "\n\nهل ساعدك هذا؟ (نعم / لا)"
            log_message(self.log_file, "bot", response)
            return response

    def reset(self):
        self.collected = []
        self.current_index = 0
        self.finished = False
        self.feedback_stage = False
        self.waiting_for_feedback = False
        self.corrected_drug = None
        self.last_prediction = None
        self.last_input_text = ""
        self.session_id, self.log_file = start_new_session()

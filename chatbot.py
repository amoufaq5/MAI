from session_logger import start_new_session, log_message, log_final_recommendation
from model import predict_drug
from response_templates import make_human_response
from langdetect import detect
from user_profile import save_user_profile
from feedback_collector import store_feedback


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
                response = "What drug did you

from session_logger import start_new_session, log_message, log_final_recommendation
from model import predict_drug
from response_templates import make_human_response
from langdetect import detect


class ChatBot:
    def __init__(self, model, vectorizer, encoder, df):
        self.model = model
        self.vectorizer = vectorizer
        self.encoder = encoder
        self.df = df

        # English ASMETHOD questions
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

        # Arabic ASMETHOD questions
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
        self.lang = "en"
        self.session_id, self.log_file = start_new_session()

    def handle_message(self, message):
        log_message(self.log_file, "user", message)

        # Detect language
        try:
            self.lang = detect(message)
        except:
            self.lang = "en"

        # Choose appropriate language for questions
        self.questions = self.questions_ar if self.lang == "ar" else self.questions_en

        if self.finished:
            self.reset()
            response = "ابدأ من جديد بكتابة 'start'" if self.lang == "ar" else "Type 'start' to begin a new diagnosis."
            log_message(self.log_file, "bot", response)
            return response

        if message.lower() == 'start':
            self.reset()
            self.questions = self.questions_ar if self.lang == "ar" else self.questions_en
            response = self.questions[0]
            log_message(self.log_file, "bot", response)
            return response

        if self.current_index < len(self.questions):
            self.collected.append(message)
            self.current_index += 1

        if self.current_index < len(self.questions):
            response = self.questions[self.current_index]
            log_message(self.log_file, "bot", response)
            return response
        else:
            # All questions answered — generate prediction
            full_input = " ".join(self.collected)
            drug, confidence, side_effects = predict_drug(
                full_input, self.model, self.vectorizer, self.encoder, self.df
            )
            self.finished = True

            response = make_human_response(drug, confidence, side_effects, lang=self.lang)

            log_final_recommendation(self.log_file, drug, confidence, side_effects)
            log_message(self.log_file, "bot", response)
            return response

    def reset(self):
        self.collected = []
        self.current_index = 0
        self.finished = False
        self.session_id, self.log_file = start_new_session()

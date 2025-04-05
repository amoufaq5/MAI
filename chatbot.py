from model import predict_diagnosis

class ChatBot:
    def __init__(self, model, vectorizer):
        self.model = model
        self.vectorizer = vectorizer
        self.conversation_state = {}
        self.questions = [
            "Please provide your age and appearance (ASMETHOD: Age/appearance).",
            "Is it you or someone else experiencing the symptoms? (ASMETHOD: Self or someone else)",
            "What medications are you currently taking? (ASMETHOD: Medication)",
            "Are you taking any extra medicines? (ASMETHOD: Extra medicines)",
            "How long have these symptoms persisted? (ASMETHOD: Time persisting)",
            "Do you have any relevant medical history? (ASMETHOD: History)",
            "What other symptoms are you experiencing? (ASMETHOD: Other symptoms)",
            "Are there any danger symptoms present? (ASMETHOD: Danger symptoms)"
            # Extend with ENCORE and SIT DOWN SIR questions as needed.
        ]
        self.current_question_index = 0
        self.collected_data = []
        self.final_response_given = False

    def handle_message(self, message):
        # If conversation is complete, restart on new conversation
        if self.final_response_given:
            self.reset_conversation()

        # Allow user to explicitly start a new diagnosis session
        if message.lower() in ['start', 'begin']:
            self.reset_conversation()
            return self.questions[self.current_question_index]
        
        # Record the answer for the current question
        if self.current_question_index < len(self.questions):
            self.collected_data.append(message)
            self.current_question_index += 1
        
        # If more questions remain, ask the next one
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        else:
            # All questions answered: aggregate the responses
            aggregated_input = " ".join(self.collected_data)
            predicted_class, probabilities = predict_diagnosis(aggregated_input, self.model, self.vectorizer)
            # Interpret the prediction
            if predicted_class == 0:
                diagnosis = "Based on your responses, an OTC medication may be appropriate."
            else:
                diagnosis = "Based on your responses, it is recommended that you see a doctor for further evaluation."
            self.final_response_given = True
            # Include confidence percentages (for transparency; adjust as needed)
            response = diagnosis + " (Confidence: OTC: {:.2f}%, Refer: {:.2f}%)".format(probabilities[0]*100, probabilities[1]*100)
            return response

    def reset_conversation(self):
        self.current_question_index = 0
        self.collected_data = []
        self.final_response_given = False

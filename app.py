from flask import Flask, request, render_template, jsonify
import os
from model import load_trained_model, predict_diagnosis
from chatbot import ChatBot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secure_secret_key_here'  # Use a secure, random secret key in production

# HIPAA Notice:
# In production, ensure secure sessions, HTTPS, and encrypted data storage/transmission.
# Additional measures (e.g., access control, audit logging) must be implemented.

# Load the trained TensorFlow model and text vectorizer (assumed saved in model/ folder)
model, vectorizer = load_trained_model()

# Initialize the chatbot with the model (for diagnosis) and the vectorizer (for text processing)
chatbot = ChatBot(model, vectorizer)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    # Process user message with our chatbot logic (questionnaire + diagnosis)
    response = chatbot.handle_message(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    # For HIPAA compliance in production, run behind a secure WSGI server (e.g., Gunicorn) with HTTPS.
    app.run(host='0.0.0.0', port=5000, debug=True)

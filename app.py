from flask import Flask, request, render_template, jsonify
from model import load_trained_model
from chatbot import ChatBot

app = Flask(__name__)
from data_loader import load_dataset
...

model, vectorizer, encoder = load_trained_model()
df = load_dataset('data/dataset.csv')  # Make sure this is the correct path
chatbot = ChatBot(model, vectorizer, encoder, df)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response = chatbot.handle_message(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

CHAT_FILE = "chat_log.json"

app = Flask(__name__)

if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

@app.route("/chat/send", methods=["POST"])
def send_message():
    data = request.get_json()
    username = data.get("username")
    message = data.get("message")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not username or not message:
        return jsonify({"status": "error", "msg": "Missing fields."}), 400

    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        chat = json.load(f)

    chat.append({"username": username, "message": message, "timestamp": timestamp})

    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat, f, indent=2)

    return jsonify({"status": "success"})

@app.route("/chat/fetch")
def fetch_messages():
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        chat = json.load(f)
    return jsonify(chat)

@app.route("/chat")
def chat_ui():
    return '''
    <!DOCTYPE html>
    <html><head><title>Doctor Chat</title>
    <script>
        async function fetchMessages() {
            const res = await fetch("/chat/fetch");
            const data = await res.json();
            const box = document.getElementById("chat-box");
            box.innerHTML = data.map(m => `<p><strong>${m.username}</strong>: ${m.message} <em>(${m.timestamp})</em></p>`).join("");
        }

        async function sendMessage() {
            const user = document.getElementById("user").value;
            const msg = document.getElementById("msg").value;
            await fetch("/chat/send", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: user, message: msg})
            });
            document.getElementById("msg").value = "";
            fetchMessages();
        }

        setInterval(fetchMessages, 2000);
        window.onload = fetchMessages;
    </script></head>
    <body style="font-family:sans-serif; margin:30px">
        <h2>Doctor Chat Room</h2>
        <input id="user" placeholder="Username" style="margin-bottom:10px"><br>
        <div id="chat-box" style="border:1px solid #ccc; padding:10px; height:300px; overflow-y:scroll; background:#f4f4f4"></div>
        <input id="msg" placeholder="Your message" style="width:70%">
        <button onclick="sendMessage()">Send</button>
    </body></html>
    '''

if __name__ == "__main__":
    app.run(port=7001, debug=True)

from flask import Flask, render_template_string, request, send_file, redirect, url_for, session
import json
import os
import pandas as pd
from collections import Counter
from user_auth import authenticate_user, change_password, init_user_db
from user_manager import list_users, add_user, delete_user

app = Flask(__name__)
app.secret_key = "your-secret-key"
init_user_db()

CHAT_FILE = "chat_log.json"
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MYD Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial; background: #121212; color: #f8f8f8; margin: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #444; text-align: left; }
        th { background: #007bff; color: white; }
        tr:nth-child(even) { background: #222; }
        a, button { color: #0af; text-decoration: none; cursor: pointer; background: none; border: none; }
        .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .charts { display: flex; gap: 40px; margin: 20px 0; }
        #chat { border: 1px solid #444; padding: 10px; max-height: 200px; overflow-y: scroll; background: #1e1e1e; margin-top: 40px; }
        input, select { padding: 5px; margin-right: 5px; }
    </style>
</head>
<body>
    <div class="topbar">
        <div>
            <h1>MYD Referral Dashboard</h1>
            <form method="get" action="/">
                <input type="text" name="q" placeholder="Search symptoms or drug" value="{{ query }}">
                <button type="submit">Search</button>
                {% if session['role'] == 'admin' %}
                    <a href="/export">Export to Excel</a>
                    <a href="/users">Manage Users</a>
                {% endif %}
                <a href="/change-password">Change Password</a>
                <a href="/logout">Logout</a>
            </form>
        </div>
    </div>

    <div class="charts">
        <div>
            <h3>Top Drugs</h3>
            <canvas id="drugChart"></canvas>
        </div>
        <div>
            <h3>Top Symptoms</h3>
            <canvas id="symptomChart"></canvas>
        </div>
    </div>

    <table>
        <thead>
            <tr><th>Session ID</th><th>Date/Time</th><th>Symptoms</th><th>Drug</th><th>Confidence</th><th>PDF</th></tr>
        </thead>
        <tbody>
        {% for entry in data %}
            <tr>
                <td>{{ entry.session_id }}</td>
                <td>{{ entry.timestamp }}</td>
                <td>{{ entry.symptoms }}</td>
                <td>{{ entry.recommended_drug }}</td>
                <td>{{ entry.confidence }}%</td>
                <td><a href="/pdf/{{ entry.session_id }}" target="_blank">Download</a></td>
            </tr>
        {% endfor %}
        </tbody>
    </table>

    <h3>Doctor Chat</h3>
    <div id="chat"></div>
    <input id="chat_user" placeholder="Your name">
    <input id="chat_msg" placeholder="Type message">
    <button onclick="sendMsg()">Send</button>

    <script>
        const drugData = {{ top_drugs | safe }};
        const symptomData = {{ top_symptoms | safe }};

        new Chart(document.getElementById('drugChart'), {
            type: 'bar',
            data: {
                labels: drugData.labels,
                datasets: [{ label: 'Top Drugs', data: drugData.values, backgroundColor: '#007bff' }]
            }
        });

        new Chart(document.getElementById('symptomChart'), {
            type: 'bar',
            data: {
                labels: symptomData.labels,
                datasets: [{ label: 'Top Symptoms', data: symptomData.values, backgroundColor: '#28a745' }]
            }
        });

        async function loadChat() {
            const res = await fetch('/chat/fetch');
            const data = await res.json();
            document.getElementById('chat').innerHTML = data.map(x => `<p><b>${x.username}</b>: ${x.message} <small>(${x.timestamp})</small></p>`).join('');
        }

        async function sendMsg() {
            const user = document.getElementById('chat_user').value;
            const msg = document.getElementById('chat_msg').value;
            if (!user || !msg) return;
            await fetch('/chat/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: user, message: msg})
            });
            document.getElementById('chat_msg').value = "";
            loadChat();
        }

        setInterval(loadChat, 2000);
        loadChat();
    </script>
</body>
</html>
"""

@app.route("/")
def dashboard():
    if not session.get("authenticated"):
        return redirect("/login")

    query = request.args.get("q", "").strip().lower()
    with open("referrals.json", encoding="utf-8") as f:
        data = json.load(f)

    if query:
        data = [d for d in data if query in d["symptoms"].lower() or query in d["recommended_drug"].lower()]

    drug_counter = Counter(d["recommended_drug"] for d in data)
    top_drugs = drug_counter.most_common(5)
    top_drugs_dict = {"labels": [x[0] for x in top_drugs], "values": [x[1] for x in top_drugs]}

    symptoms = " ".join(d["symptoms"] for d in data).lower().replace(",", " ").split()
    top_symptoms = Counter(symptoms).most_common(5)
    top_symptoms_dict = {"labels": [x[0] for x in top_symptoms], "values": [x[1] for x in top_symptoms]}

    return render_template_string(TEMPLATE, data=reversed(data), query=query,
                                  top_drugs=top_drugs_dict, top_symptoms=top_symptoms_dict)

@app.route("/chat/fetch")
def fetch_chat():
    with open(CHAT_FILE, encoding="utf-8") as f:
        return json.dumps(json.load(f))

@app.route("/chat/send", methods=["POST"])
def send_chat():
    data = request.get_json()
    entry = {
        "username": data.get("username"),
        "message": data.get("message"),
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(CHAT_FILE, encoding="utf-8") as f:
        chat = json.load(f)
    chat.append(entry)
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat, f, indent=2)
    return "ok"

# ... (rest of your routes unchanged)

if __name__ == "__main__":
    app.run(port=7000, debug=True)

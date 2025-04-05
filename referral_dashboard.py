from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, jsonify
import json
import os
import pandas as pd
from collections import Counter
from user_auth import authenticate_user, change_password, init_user_db, hash_password
from user_manager import list_users, add_user, delete_user
from flask_mail import Mail, Message
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"
init_user_db()

# Email setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Change this
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Change this
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Change this
mail = Mail(app)

CHAT_FILE = "chat_log.json"
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if add_user(username, password, role):
            return redirect("/login")
        return "Username already exists", 400

    return render_template_string("""
    <html><body style='text-align:center;'>
    <h2>Register</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <input type="password" name="password" placeholder="Password"><br><br>
        <select name="role"><option value='doctor'>Doctor</option><option value='admin'>Admin</option></select><br><br>
        <button type="submit">Register</button>
    </form>
    <a href='/login'>Already have an account? Login</a>
    </body></html>
    """)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return "Please provide a username", 400
        reset_token = str(uuid.uuid4())

        # Send reset link via email
        msg = Message("Password Reset Request", recipients=[username])
        reset_link = f"http://localhost:7000/reset-password/{reset_token}"
        msg.body = f"Click the link to reset your password: {reset_link}"
        mail.send(msg)

        return f"Password reset link sent to {username}. Check your email."

    return render_template_string("""
    <html><body style='text-align:center;'>
    <h2>Forgot Password</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <button type="submit">Send Reset Link</button>
    </form>
    </body></html>
    """)

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        new_password = request.form.get("new_password")
        # Here you would match token to a user and reset their password
        return "Password successfully updated. Please log in."

    return render_template_string("""
    <html><body style='text-align:center;'>
    <h2>Reset Password</h2>
    <form method="post">
        <input type="password" name="new_password" placeholder="New Password"><br><br>
        <button type="submit">Reset Password</button>
    </form>
    </body></html>
    """)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = authenticate_user(username, password)
        if role:
            session["authenticated"] = True
            session["user"] = username
            session["role"] = role
            return redirect("/")
        return "Invalid username or password", 403

    return render_template_string("""
    <html><body style='text-align:center;margin-top:100px;font-family:sans-serif;'>
    <h2>Login</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <input type="password" name="password" placeholder="Password"><br><br>
        <button type="submit">Login</button>
    </form>
    </body></html>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

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

    with open("dashboard_template.html", encoding="utf-8") as f:
        html_template = f.read()
    return render_template_string(html_template, data=reversed(data), query=query,
                                  top_drugs=top_drugs_dict, top_symptoms=top_symptoms_dict)

@app.route("/chat/fetch")
def fetch_chat():
    with open(CHAT_FILE, encoding="utf-8") as f:
        return jsonify(json.load(f))

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

if __name__ == "__main__":
    app.run(port=7000, debug=True)

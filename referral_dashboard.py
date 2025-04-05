from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, jsonify
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

@app.route("/export")
def export_excel():
    if session.get("role") != "admin":
        return "Unauthorized", 403
    with open("referrals.json", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    file_path = "referrals_export.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

@app.route("/users", methods=["GET", "POST"])
def manage_users():
    if session.get("role") != "admin":
        return "Unauthorized", 403

    message = ""
    if request.method == "POST":
        if request.form.get("action") == "add":
            if add_user(request.form["username"], request.form["password"], request.form["role"]):
                message = "✅ User added."
            else:
                message = "❌ Username already exists."
        elif request.form.get("action") == "delete":
            if delete_user(request.form["username"]):
                message = "🗑️ User deleted."
            else:
                message = "❌ User not found."

    users = list_users()
    user_list = "".join([f"<li>{u['username']} ({u['role']})</li>" for u in users])
    return render_template_string(f"""
    <!DOCTYPE html>
    <html><head><title>User Manager</title></head>
    <body style='font-family:sans-serif;'>
        <h2>Manage Users</h2>
        <form method='post'>
            <input name='username' placeholder='Username'>
            <input name='password' placeholder='Password'>
            <select name='role'><option value='doctor'>Doctor</option><option value='admin'>Admin</option></select>
            <button name='action' value='add'>Add User</button>
        </form><br>
        <form method='post'>
            <input name='username' placeholder='Username'>
            <button name='action' value='delete'>Delete User</button>
        </form><br>
        <p>{message}</p>
        <h3>All Users</h3>
        <ul>{user_list}</ul>
        <a href='/'>&larr; Back</a>
    </body></html>
    """)

@app.route("/pdf/<session_id>")
def download_pdf(session_id):
    pdf_path = f"referral_letters/referral_{session_id}.pdf"
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "PDF not found", 404

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
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><title>Login</title></head>
    <body style='text-align:center;margin-top:100px;font-family:sans-serif;'>
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

@app.route("/change-password", methods=["GET", "POST"])
def change_pw():
    if not session.get("authenticated"):
        return redirect("/login")

    message = ""
    if request.method == "POST":
        new_pw = request.form.get("new_password")
        if change_password(session["user"], new_pw):
            message = "✅ Password changed successfully."
        else:
            message = "❌ Error changing password."

    return render_template_string(f"""
    <!DOCTYPE html>
    <html><head><title>Change Password</title></head>
    <body style='text-align:center;margin-top:100px;font-family:sans-serif;'>
        <h2>Change Password for {session['user']}</h2>
        <form method="post">
            <input type="password" name="new_password" placeholder="New Password">
            <button type="submit">Change</button>
        </form>
        <p>{message}</p>
        <a href='/'>⟵ Back</a>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(port=7000, debug=True)

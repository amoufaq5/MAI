from flask import Flask, render_template_string, request, send_file, redirect, url_for, session
import json
import os
import pandas as pd
from user_auth import authenticate_user, change_password, init_user_db

app = Flask(__name__)
app.secret_key = "your-secret-key"
init_user_db()

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MYD Referrals Dashboard</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f8f9fa; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
        th { background: #007bff; color: white; }
        tr:nth-child(even) { background: #f2f2f2; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .topbar { display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="topbar">
        <h1>MYD Referral Logs</h1>
        <form method="get" action="/">
            <input type="text" name="q" placeholder="Search symptoms or drug" value="{{ query }}">
            <button type="submit">Search</button>
            <a href="/export" style="margin-left: 20px;">Export to Excel</a>
            <a href="/change-password" style="margin-left: 20px;">Change Password</a>
            <a href="/logout" style="margin-left: 20px;">Logout</a>
        </form>
    </div>
    <table>
        <thead>
            <tr>
                <th>Session ID</th>
                <th>Date/Time</th>
                <th>Symptoms</th>
                <th>Recommended Drug</th>
                <th>Confidence</th>
                <th>PDF</th>
            </tr>
        </thead>
        <tbody>
            {% for entry in data %}
            <tr>
                <td>{{ entry.session_id }}</td>
                <td>{{ entry.timestamp }}</td>
                <td>{{ entry.symptoms }}</td>
                <td>{{ entry.recommended_drug }}</td>
                <td>{{ entry.confidence }}%</td>
                <td>
                    <a href="/pdf/{{ entry.session_id }}" target="_blank">Download</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>Login</title></head>
<body style="font-family:sans-serif; text-align:center; margin-top:100px">
<h2>Login</h2>
<form method="post">
    <input name="username" placeholder="Username"><br><br>
    <input type="password" name="password" placeholder="Password"><br><br>
    <button type="submit">Login</button>
</form>
</body>
</html>
"""

CHANGE_PASSWORD_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>Change Password</title></head>
<body style="font-family:sans-serif; text-align:center; margin-top:100px">
<h2>Change Password for {{ user }}</h2>
<form method="post">
    <input type="password" name="new_password" placeholder="New Password">
    <button type="submit">Change</button>
</form>
{% if message %}<p>{{ message }}</p>{% endif %}
<a href="/">⬅ Back</a>
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

    return render_template_string(TEMPLATE, data=reversed(data), query=query)

@app.route("/pdf/<session_id>")
def download_pdf(session_id):
    pdf_path = f"referral_letters/referral_{session_id}.pdf"
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "PDF not found", 404

@app.route("/export")
def export_excel():
    with open("referrals.json", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    file_path = "referrals_export.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

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
    return render_template_string(LOGIN_TEMPLATE)

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

    return render_template_string(CHANGE_PASSWORD_TEMPLATE, user=session["user"], message=message)

if __name__ == "__main__":
    app.run(port=7000, debug=True)

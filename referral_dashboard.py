from flask import Flask, render_template, request, redirect, url_for, session
from user_auth import authenticate_user, init_user_db, get_all_users, add_user, delete_user
from chatbot import ChatBot
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong key

# Initialize user database
init_user_db()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = authenticate_user(username, password)
        if role:
            session['username'] = username
            session['role'] = role
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot_ui():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'chatbot' not in session:
        bot = ChatBot(username=session['username'])
        session['chatbot'] = bot.__dict__
    else:
        bot = ChatBot(username=session['username'])
        bot.__dict__.update(session['chatbot'])

    user_input = None
    bot_reply = None

    if request.method == 'POST':
        user_input = request.form['message']
        bot_reply = bot.handle_message(user_input)
        session['chatbot'] = bot.__dict__

    return render_template('chatbot.html', user_input=user_input, bot_reply=bot_reply)

@app.route('/admin/users')
def admin_users():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    users = get_all_users()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
def admin_add_user():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    add_user(username, password, role)
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<username>')
def admin_delete_user(username):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    delete_user(username)
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

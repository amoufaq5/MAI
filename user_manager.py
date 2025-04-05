import json
import os
import hashlib

USER_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def add_user(username, password, role="doctor"):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    save_users(users)
    return True

def delete_user(username):
    users = load_users()
    if username in users:
        users.pop(username)
        save_users(users)
        return True
    return False

def list_users():
    users = load_users()
    return [{"username": k, "role": v["role"]} for k, v in users.items()]

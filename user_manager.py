import json
import os
import bcrypt

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def add_user(username, password, role):
    users = load_users()

    # Check if username already exists
    for user in users:
        if user["username"] == username:
            return False

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users.append({
        "username": username,
        "password": hashed_pw,
        "role": role
    })
    save_users(users)
    return True

def list_users():
    users = load_users()
    return [{"username": u["username"], "role": u["role"]} for u in users]  # Hide passwords

def delete_user(username):
    users = load_users()
    new_users = [u for u in users if u["username"] != username]
    if len(new_users) == len(users):
        return False  # Not found
    save_users(new_users)
    return True

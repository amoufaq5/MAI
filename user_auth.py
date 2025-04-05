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

def authenticate_user(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username:
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return user["role"]
    return None

def change_password(username, new_password):
    users = load_users()
    for user in users:
        if user["username"] == username:
            user["password"] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            save_users(users)
            return True
    return False

def init_user_db():
    if not os.path.exists(USERS_FILE):
        save_users([])

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

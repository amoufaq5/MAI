import json
import os
import bcrypt

USERS_FILE = "users.json"

def init_user_db():
    if not os.path.exists(USERS_FILE):
        default_users = [
            {"username": "admin", "password": hash_password("admin123"), "role": "admin"},
            {"username": "doctor", "password": hash_password("doctor123"), "role": "doctor"}
        ]
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def authenticate_user(username, password):
    if not os.path.exists(USERS_FILE):
        return None
    with open(USERS_FILE, encoding="utf-8") as f:
        users = json.load(f)
    for user in users:
        if user["username"] == username:
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return user["role"]
    return None

def change_password(username, new_password):
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, encoding="utf-8") as f:
        users = json.load(f)
    updated = False
    for user in users:
        if user["username"] == username:
            user["password"] = hash_password(new_password)
            updated = True
            break
    if updated:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    return updated

def authenticate_user(username, password):
    if not os.path.exists(USERS_FILE):
        return None

    try:
        with open(USERS_FILE, encoding="utf-8") as f:
            users = json.load(f)
    except json.JSONDecodeError as e:
        print("Error loading JSON:", e)
        return None

    print("Users loaded:", users)  # Debugging to check if it's a list of dictionaries
    for user in users:
        print("Checking user:", user)  # Debugging to check the user object
        if user["username"] == username:
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return user["role"]
    return None




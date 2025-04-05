import json
import os
import bcrypt

USERS_FILE = "users.json"

def add_user(username, password, role):
    users = []

    # Load existing users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, encoding="utf-8") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                pass

    # Check if username already exists
    for user in users:
        if user["username"] == username:
            return False  # Username already exists

    # Hash password and add user
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users.append({
        "username": username,
        "password": hashed_pw,
        "role": role
    })

    # Save updated list
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

    return True

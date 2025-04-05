import json
import os
import hashlib

USER_FILE = "users.json"

# Create initial admin if file doesn't exist
def init_user_db():
    if not os.path.exists(USER_FILE):
        default_user = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin"
            },
            "doctor": {
                "password": hash_password("doctor123"),
                "role": "doctor"
            }
        }
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(default_user, f, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(username, password):
    with open(USER_FILE, encoding="utf-8") as f:
        users = json.load(f)
    user = users.get(username)
    if user and user["password"] == hash_password(password):
        return user["role"]
    return None


def change_password(username, new_password):
    with open(USER_FILE, encoding="utf-8") as f:
        users = json.load(f)
    if username in users:
        users[username]["password"] = hash_password(new_password)
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return True
    return False


if __name__ == "__main__":
    init_user_db()

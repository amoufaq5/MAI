import json
import os
import hashlib

USER_FILE = "users.json"

# Create initial users if file doesn't exist
def init_user_db():
    if not os.path.exists(USER_FILE):
        default_user = {
            "admin": {
                "password": "1b6adbe6d85d43cba3fa6932a24cd3f9c8ed8a2c36b64641ed6b6828f50f57e1",
                "role": "admin"
            },
            "doctor": {
                "password": "e7e0fcfbe8340422f59bb04d90e6c6c2a536ab0f11d3c0b96b01a51772f1f6d8",
                "role": "doctor"
            }
        }
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(default_user, f, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(username, password):
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE, encoding="utf-8") as f:
        users = json.load(f)
    user = users.get(username)
    if user and user["password"] == hash_password(password):
        return user["role"]
    return None


def change_password(username, new_password):
    if not os.path.exists(USER_FILE):
        return False
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

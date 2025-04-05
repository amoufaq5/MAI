import json
import bcrypt
import os

USER_DB_FILE = 'users.json'

# Initialize user database if it doesn't exist
def init_user_db():
    if not os.path.exists(USER_DB_FILE):
        default_users = {
            "admin": {
                "password": bcrypt.hashpw("admin1234".encode(), bcrypt.gensalt()).decode(),
                "role": "admin"
            },
            "doctor": {
                "password": bcrypt.hashpw("doctor1234".encode(), bcrypt.gensalt()).decode(),
                "role": "doctor"
            }
        }
        with open(USER_DB_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)

# Authenticate a user
def authenticate_user(username, password):
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    user = users.get(username)
    if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
        return user['role']
    return None

# Get all users for admin listing
def get_all_users():
    with open(USER_DB_FILE, 'r') as f:
        return json.load(f)

# Add new user
def add_user(username, password, role):
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    if username in users:
        return False
    users[username] = {
        "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        "role": role
    }
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    return True

# Delete a user
def delete_user(username):
    with open(USER_DB_FILE, 'r') as f:
        users = json.load(f)
    if username in users:
        del users[username]
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    return False

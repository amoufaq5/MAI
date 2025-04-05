import json

with open("users.json", encoding="utf-8") as f:
    users = json.load(f)
    print("Users loaded:", users)
    for user in users:
        print(user["username"], user["role"])

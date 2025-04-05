from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
STORAGE_DIR = "ehr_mock_storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.route("/ehr/receive", methods=["POST"])
def receive_fhir():
    try:
        bundle = request.json
        session_id = bundle.get("id") or datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(STORAGE_DIR, f"received_{session_id}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success", "message": "FHIR bundle received and saved."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=6000, debug=True)

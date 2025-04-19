import sys
import json
from pathlib import Path

def clean_and_save(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        if input_path.endswith(".json"):
            data = json.load(f)
        elif input_path.endswith(".csv"):
            import pandas as pd
            data = pd.read_csv(input_path).to_dict(orient="records")
        elif input_path.endswith(".txt"):
            text = f.read()
            data = [{"text": line.strip()} for line in text.splitlines() if line.strip()]
        else:
            print(f"❌ Unsupported file format: {input_path}")
            return

    # Very basic clean logic
    cleaned_data = []
    for entry in data:
        text = json.dumps(entry, ensure_ascii=False)
        cleaned_data.append({"text": text.replace("\n", " ").strip()})

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    clean_and_save(input_file, output_file)

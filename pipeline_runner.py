import os
import subprocess
from pathlib import Path

RAW_DIR = Path("data/kaggle/raw")
FORMATTED_DIR = Path("data/kaggle/formatted")
FORMATTED_DIR.mkdir(parents=True, exist_ok=True)

scripts = [
    ("clean_text.py", "_cleaned.json"),
    ("tag_symptoms.py", "_cleaned_tagged.json"),
    ("convert_to_jsonl.py", ".jsonl")
]

files = list(RAW_DIR.glob("*.json"))

for input_file in files:
    print(f"\n🔄 Processing {input_file}...")
    base = input_file.stem
    current_path = input_file

    for script, suffix in scripts:
        next_path = RAW_DIR / (base + suffix)
        try:
            subprocess.run(["python", script, str(current_path), str(next_path)], check=True)
        except subprocess.CalledProcessError:
            print(f"❌ Error running {script} on {current_path.name}")
            break
        current_path = next_path

    # Final output path
    if current_path.exists():
        formatted_output = FORMATTED_DIR / current_path.name
        current_path.rename(formatted_output)
        print(f"✅ Final formatted file saved to: {formatted_output}")
    else:
        print(f"⚠️ Final output file not found for {input_file.name}")

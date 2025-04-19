import os
import subprocess
from pathlib import Path

RAW_DIR = Path("data/kaggle/raw")
FORMATTED_DIR = Path("data/kaggle/formatted")

FORMATTED_DIR.mkdir(parents=True, exist_ok=True)

for file in RAW_DIR.glob("*.*"):
    name = file.stem

    cleaned_path = RAW_DIR / f"{name}_cleaned.json"
    tagged_path = RAW_DIR / f"{name}_cleaned_tagged.json"
    formatted_path = FORMATTED_DIR / f"{name}.jsonl"

    print(f"🔄 Processing {file}...")

    try:
        subprocess.run(["python", "clean_text.py", str(file), str(cleaned_path)], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error running clean_text.py on {file.name}")

    try:
        subprocess.run(["python", "tag_symptoms.py", str(cleaned_path), str(tagged_path)], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error running tag_symptoms.py on {cleaned_path.name}")

    try:
        subprocess.run(["python", "convert_to_jsonl.py", str(tagged_path), str(formatted_path)], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error running convert_to_jsonl.py on {tagged_path.name}")

    print(f"✅ Final formatted file saved to: {formatted_path}\n")

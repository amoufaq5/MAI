# pipeline_runner.py
import os
from pathlib import Path
import subprocess

# List of example raw scraped files to process
target_files = [
    "data/webmd/raw/Flu_Symptoms_and_Treatment_-_WebMD.json",
    "data/cdc/raw/Flu_Symptoms_-_CDC.json",
    "data/who/raw/Influenza_(Seasonal)_-_WHO.json",
    "data/openfda/raw/openfda_labels.json",
    "data/pubmed/raw/diabetes_symptoms.json",
    "data/dailymed/raw/paracetamol.json"
]

# Run steps: clean → tag → jsonl
for file_path in target_files:
    print(f"🔄 Processing {file_path}...")
    base = Path(file_path).stem.replace(".json", "")

    cleaned_path = file_path.replace(".json", "_cleaned.json")
    tagged_path = file_path.replace(".json", "_cleaned_tagged.json")
    formatted_path = file_path.replace("raw", "formatted").replace(".json", ".jsonl")
    os.makedirs(Path(formatted_path).parent, exist_ok=True)

    subprocess.run(["python", "clean_text.py", file_path, cleaned_path])
    subprocess.run(["python", "tag_symptoms.py", cleaned_path, tagged_path])
    subprocess.run(["python", "convert_to_jsonl.py", tagged_path, formatted_path])

    print(f"✅ Final formatted file saved to: {formatted_path}\n")

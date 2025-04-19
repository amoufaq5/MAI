import os
from pathlib import Path
import subprocess

# Define data sources
sources = ["webmd", "cdc", "who", "openfda", "pubmed", "dailymed"]
base_dir = Path("data")

def run_step(script, input_path, output_path):
    try:
        subprocess.run(["python", script, input_path, output_path], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error running {script} on {input_path}")

def run_pipeline():
    for source in sources:
        raw_dir = base_dir / source / "raw"
        formatted_dir = base_dir / source / "formatted"
        formatted_dir.mkdir(parents=True, exist_ok=True)

        for file in raw_dir.glob("*.json"):
            base_name = file.stem

            print(f"🔄 Processing {file}...")

            cleaned = raw_dir / f"{base_name}_cleaned.json"
            tagged = raw_dir / f"{base_name}_cleaned_tagged.json"
            final = formatted_dir / f"{base_name}.jsonl"

            # Step 1: Clean
            run_step("clean_text.py", str(file), str(cleaned))

            # Step 2: Tag
            run_step("tag_symptoms.py", str(cleaned), str(tagged))

            # Step 3: Convert
            run_step("convert_to_jsonl.py", str(tagged), str(final))

            print(f"✅ Final formatted file saved to: {final}")

if __name__ == "__main__":
    run_pipeline()

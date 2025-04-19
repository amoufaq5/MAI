# convert_to_jsonl.py
import json
import os

def convert_to_jsonl(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    with open(output_path, "w", encoding="utf-8") as f:
        for entry in data:
            text = entry.get("cleaned") or entry.get("content") or entry.get("label")
            tags = entry.get("tags", [])
            source = entry.get("source", "unknown")

            jsonl_entry = {
                "input": f"[SOURCE: {source}]\n{text.strip()[:2000]}",
                "output": ", ".join(tags) if tags else "unknown"
            }
            f.write(json.dumps(jsonl_entry) + "\n")

if __name__ == '__main__':
    input_file = "data/webmd/raw/Flu_Symptoms_and_Treatment_cleaned_tagged.json"
    output_file = "data/webmd/formatted/Flu_Symptoms_and_Treatment.jsonl"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    convert_to_jsonl(input_file, output_file)
    print("✅ Converted to JSONL for LLM training.")

# clean_text.py
import re

def basic_clean(text):
    text = text.replace("\xa0", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)  # remove excess spaces
    text = re.sub(r"\[[^\]]*\]", "", text)  # remove citations like [1], [a]
    text = re.sub(r"https?://\S+", "", text)  # remove links
    text = re.sub(r"[\r\n\t]", " ", text)
    text = text.strip()
    return text

def clean_and_save(input_path, output_path):
    import json
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, list):
        for entry in raw:
            if "content" in entry:
                entry["cleaned"] = basic_clean(entry["content"])
            elif "abstract" in entry:
                entry["cleaned"] = basic_clean(entry.get("abstract", ""))
            elif "label" in entry:
                entry["cleaned"] = basic_clean(entry.get("label", ""))
    else:
        raw["cleaned"] = basic_clean(raw.get("content") or raw.get("abstract") or raw.get("label") or "")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)

if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    input_file = "data/webmd/raw/Flu_Symptoms_and_Treatment_-_WebMD.json"
    output_file = Path(input_file).with_name("Flu_Symptoms_and_Treatment_cleaned.json")
    clean_and_save(input_file, str(output_file))
    print("✅ Cleaned and saved.")

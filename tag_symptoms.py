import sys
import json
import spacy

nlp = spacy.load("en_core_web_sm")

def tag_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tagged = []
    for entry in data:
        text = entry["text"]
        doc = nlp(text)
        symptoms = [ent.text for ent in doc.ents if ent.label_ in ["SYMPTOM", "DISEASE", "CONDITION"]]
        tagged.append({"text": text, "symptoms": symptoms})

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tagged, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    tag_file(input_path, output_path)

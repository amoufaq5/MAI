import sys
import json

def convert_to_jsonl(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    convert_to_jsonl(input_path, output_path)

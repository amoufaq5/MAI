# openfda_scraper.py
import requests
import os
import json

def fetch_openfda_drug_labels(limit=100):
    url = f"https://api.fda.gov/drug/label.json?limit={limit}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        items = res.json().get("results", [])
    except Exception as e:
        print("[ERROR] Failed to fetch OpenFDA data:", e)
        return []

    extracted = []
    for item in items:
        label = {
            "id": item.get("id"),
            "brand_name": item.get("openfda", {}).get("brand_name", ["Unknown"])[0],
            "generic_name": item.get("openfda", {}).get("generic_name", ["Unknown"])[0],
            "purpose": " ".join(item.get("purpose", [])),
            "indications_and_usage": " ".join(item.get("indications_and_usage", [])),
            "warnings": " ".join(item.get("warnings", [])),
            "adverse_reactions": " ".join(item.get("adverse_reactions", [])),
            "dosage_and_administration": " ".join(item.get("dosage_and_administration", []))
        }
        extracted.append(label)

    return extracted


def save_results(data, name="openfda_labels"):
    os.makedirs("data/openfda/raw", exist_ok=True)
    with open(f"data/openfda/raw/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    print("🔍 Scraping OpenFDA drug labels (limit=100)...")
    data = fetch_openfda_drug_labels(limit=100)
    save_results(data)
    print(f"✅ Saved {len(data)} entries to data/openfda/raw/")

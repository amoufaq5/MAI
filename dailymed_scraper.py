# dailymed_scraper.py
import requests
import os
import json
from bs4 import BeautifulSoup

def search_dailymed(query, limit=5):
    search_url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={query}"
    res = requests.get(search_url)
    if res.status_code != 200:
        print(f"[ERROR] Failed to search DailyMed: {res.status_code}")
        return []
    results = res.json().get("data", [])[:limit]
    return results

def fetch_document(setid):
    url = f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={setid}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    soup = BeautifulSoup(res.text, "html.parser")
    content = soup.find("div", id="content")
    return content.get_text(separator=" ", strip=True) if content else None

def save_result(query, docs):
    os.makedirs("data/dailymed/raw", exist_ok=True)
    with open(f"data/dailymed/raw/{query.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)

if __name__ == "__main__":
    query = "paracetamol"
    results = search_dailymed(query)
    output = []
    for r in results:
        setid = r.get("setid")
        label = fetch_document(setid)
        if label:
            output.append({"setid": setid, "title": r.get("title"), "label": label})

    save_result(query, output)
    print(f"✅ Saved {len(output)} DailyMed entries for '{query}'")

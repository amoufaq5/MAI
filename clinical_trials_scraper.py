# clinical_trials_scraper.py
import requests
import os
import json

def fetch_trials(query, max_results=20):
    url = f"https://clinicaltrials.gov/api/query/study_fields?expr={query}&fields=NCTId,BriefTitle,Condition,BriefSummary&min_rnk=1&max_rnk={max_results}&fmt=json"
    try:
        res = requests.get(url)
        res.raise_for_status()
        studies = res.json()["StudyFieldsResponse"]["StudyFields"]
    except Exception as e:
        print("[ERROR] Failed to fetch ClinicalTrials.gov:", e)
        return []

    results = []
    for s in studies:
        results.append({
            "nct_id": s.get("NCTId", [""])[0],
            "title": s.get("BriefTitle", [""])[0],
            "condition": s.get("Condition", [""])[0] if s.get("Condition") else "",
            "summary": s.get("BriefSummary", [""])[0] if s.get("BriefSummary") else ""
        })
    return results

def save_results(query, data):
    os.makedirs("data/clinicaltrials/raw", exist_ok=True)
    path = f"data/clinicaltrials/raw/{query.replace(' ', '_')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    query = "diabetes"
    data = fetch_trials(query)
    save_results(query, data)
    print(f"✅ Saved {len(data)} clinical trial summaries for '{query}'")

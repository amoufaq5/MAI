# pubmed_scraper.py
import requests
from xml.etree import ElementTree as ET
import json
import os

def fetch_pubmed(query, max_results=100):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    r = requests.get(search_url)
    ids = r.json().get("esearchresult", {}).get("idlist", [])

    summaries = []
    for i in range(0, len(ids), 10):
        batch = ids[i:i+10]
        fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={','.join(batch)}&retmode=xml"
        res = requests.get(fetch_url)
        root = ET.fromstring(res.content)

        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", default="")
            abstract = " ".join([abst.text for abst in article.findall(".//AbstractText") if abst.text])
            pmid = article.findtext(".//PMID", default="")
            summaries.append({"pmid": pmid, "title": title, "abstract": abstract})

    return summaries


def save_results(query, data):
    os.makedirs("data/pubmed/raw", exist_ok=True)
    filename = f"data/pubmed/raw/{query.replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    search_term = "diabetes symptoms"
    results = fetch_pubmed(search_term, max_results=50)
    save_results(search_term, results)
    print(f"Saved {len(results)} articles for query '{search_term}'")

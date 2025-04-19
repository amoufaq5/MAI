# cdc_scraper.py
import requests
from bs4 import BeautifulSoup
import os
import json

def scrape_cdc_page(url):
    res = requests.get(url)
    if res.status_code != 200:
        print(f"[ERROR] Failed to fetch: {url}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    content_div = soup.find("div", class_="card-body") or soup.find("div", class_="syndicate")
    if not content_div:
        return None

    return content_div.get_text(separator=" ", strip=True)

def save_result(title, content):
    os.makedirs("data/cdc/raw", exist_ok=True)
    with open(f"data/cdc/raw/{title.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
        json.dump({"title": title, "content": content}, f, indent=2)

if __name__ == "__main__":
    url = "https://www.cdc.gov/flu/symptoms/index.html"
    title = "Flu Symptoms - CDC"
    content = scrape_cdc_page(url)
    if content:
        save_result(title, content)
        print(f"✅ Saved content for {title}")
    else:
        print("❌ Failed to extract CDC content")

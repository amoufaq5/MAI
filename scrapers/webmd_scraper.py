# webmd_scraper.py
import requests
from bs4 import BeautifulSoup
import os
import json

def scrape_webmd_article(url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        print(f"[ERROR] Failed to fetch WebMD: {res.status_code}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    content_div = soup.find("article") or soup.find("section")
    if not content_div:
        return None

    return content_div.get_text(separator=" ", strip=True)

def save_result(title, content):
    os.makedirs("data/webmd/raw", exist_ok=True)
    with open(f"data/webmd/raw/{title.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
        json.dump({"title": title, "content": content}, f, indent=2)

if __name__ == "__main__":
    url = "https://www.webmd.com/cold-and-flu/flu-symptoms-and-treatment"
    title = "Flu Symptoms and Treatment - WebMD"
    content = scrape_webmd_article(url)
    if content:
        save_result(title, content)
        print(f"✅ Saved WebMD content for {title}")
    else:
        print("❌ Failed to extract WebMD content")

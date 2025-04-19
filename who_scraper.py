# who_scraper.py
import requests
from bs4 import BeautifulSoup
import os
import json

def scrape_who_page(url):
    res = requests.get(url)
    if res.status_code != 200:
        print(f"[ERROR] Could not fetch: {url}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    article = soup.find("div", class_="sf-detail-body-wrapper")
    if not article:
        return None

    return article.get_text(separator=" ", strip=True)

def save_result(title, content):
    os.makedirs("data/who/raw", exist_ok=True)
    path = f"data/who/raw/{title.replace(' ', '_')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"title": title, "content": content}, f, indent=2)

if __name__ == "__main__":
    url = "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)"
    title = "Influenza (Seasonal) - WHO"
    content = scrape_who_page(url)
    if content:
        save_result(title, content)
        print(f"✅ Saved: {title}")
    else:
        print("❌ No content extracted.")

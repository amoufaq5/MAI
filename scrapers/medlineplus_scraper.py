# medlineplus_scraper.py
import requests
from bs4 import BeautifulSoup
import os
import json

def scrape_medlineplus(topic_url):
    res = requests.get(topic_url)
    if res.status_code != 200:
        print(f"Failed to fetch {topic_url}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    content = soup.find("div", class_="main")
    if not content:
        return None

    text = content.get_text(separator=" ", strip=True)
    return text


def save_result(title, text):
    os.makedirs("data/medlineplus/raw", exist_ok=True)
    filename = f"data/medlineplus/raw/{title.replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"title": title, "content": text}, f, indent=2)


if __name__ == "__main__":
    # Example: scrape bronchitis
    url = "https://medlineplus.gov/bronchitis.html"
    title = "Bronchitis"
    text = scrape_medlineplus(url)
    if text:
        save_result(title, text)
        print(f"✅ Saved content for {title}")
    else:
        print("❌ Failed to scrape content.")

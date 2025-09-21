from pathlib import Path
from loguru import logger
import os
import json
import requests
import wikipediaapi
from tqdm import tqdm

from sciencesage.config import (
    RAW_HTML_DIR,
    WIKI_USER_AGENT,
    WIKI_URL,
    TOPICS,
)

logger.add("logs/download_data.log", rotation="5 MB", retention="7 days")

for d in [RAW_HTML_DIR]:
    os.makedirs(d, exist_ok=True)

def save_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_image_urls(page_title, user_agent, max_images=10):
    url = f"{WIKI_URL}/w/api.php"
    params = {
        "action": "query",
        "prop": "images",
        "titles": page_title,
        "format": "json"
    }
    headers = {"User-Agent": user_agent}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return []
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    image_titles = []
    for p in pages.values():
        for img in p.get("images", []):
            if img["title"].lower().endswith((".jpg", ".jpeg", ".png", ".svg")):
                image_titles.append(img["title"])
    if not image_titles:
        return []
    image_urls = []
    for chunk_start in range(0, min(len(image_titles), max_images), 50):
        chunk = image_titles[chunk_start:chunk_start+50]
        params = {
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }
        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            continue
        img_data = resp.json()
        for img_page in img_data.get("query", {}).get("pages", {}).values():
            if "imageinfo" in img_page:
                image_urls.append(img_page["imageinfo"][0]["url"])
        if len(image_urls) >= max_images:
            break
    return image_urls[:max_images]

def download_wikipedia_raw(topic: str, user_agent: str):
    wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)
    page = wiki.page(topic)
    if not page.exists():
        logger.warning(f"Wikipedia page does not exist: {topic}")
        return
    # Save raw text
    text_fname = f"wikipedia_{topic.replace(' ', '_')}.txt"
    save_file(os.path.join(RAW_HTML_DIR, text_fname), page.text)
    # Get image URLs
    image_urls = get_image_urls(topic, user_agent)
    # Save meta data
    meta = {
        "title": page.title,
        "fullurl": page.fullurl,
        "categories": list(page.categories.keys()),
        "summary": page.summary,
        "images": image_urls,
    }
    meta_fname = f"wikipedia_{topic.replace(' ', '_')}.meta.json"
    save_json(os.path.join(RAW_HTML_DIR, meta_fname), meta)
    # Save HTML (optional, but often useful)
    html_url = f"{WIKI_URL}/api/rest_v1/page/html/{topic.replace(' ', '_')}"
    resp = requests.get(html_url, headers={"User-Agent": user_agent}, timeout=20)
    if resp.status_code == 200:
        html_fname = f"wikipedia_{topic.replace(' ', '_')}.html"
        save_file(os.path.join(RAW_HTML_DIR, html_fname), resp.text)
        logger.info(f"Saved HTML, text, and meta for {topic}")
    else:
        logger.warning(f"Failed to fetch HTML for {topic}: {resp.status_code}")

def download_category_articles(category: str, user_agent: str):
    wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)
    cat_page = wiki.page(f"Category:{category}")
    if not cat_page.exists():
        logger.warning(f"Wikipedia category does not exist: {category}")
        return 0
    count = 0
    articles = [
        (title, page)
        for title, page in cat_page.categorymembers.items()
        if page.ns == wikipediaapi.Namespace.MAIN
    ]
    for title, page in tqdm(articles, desc=f"Downloading {category} articles"):
        logger.info(f"Downloading article: {title}")
        download_wikipedia_raw(title, user_agent)
        count += 1
    return count

if __name__ == "__main__":
    total_articles = 0
    for topic in tqdm(TOPICS, desc="Topics"):
        # If topic is a category, download all articles in the category
        if topic.lower().startswith("category:"):
            category = topic.split(":", 1)[1]
            logger.info(f"Downloading all articles in category: {category}")
            count = download_category_articles(category, WIKI_USER_AGENT)
            total_articles += count
        else:
            logger.info(f"Downloading Wikipedia data for: {topic}")
            download_wikipedia_raw(topic, WIKI_USER_AGENT)
            total_articles += 1
    logger.info(f"Total number of articles downloaded: {total_articles}")

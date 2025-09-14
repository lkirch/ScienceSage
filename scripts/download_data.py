from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
import os
import requests
import wikipediaapi

from sciencesage.config import (
    RAW_DATA_DIR,
    RAW_HTML_DIR,
    RAW_IMAGES_DIR,
    RAW_PDF_DIR,
    RAW_JSON_DIR,
    NASA_API_KEY,
    NASA_APOD_API_URL,
    NASA_APOD_DAYS,
    NASA_APOD_START_DATE,
    WIKI_CRAWL_DEPTH,
    WIKI_MAX_PAGES,
    WIKI_USER_AGENT,
    ARXIV_CATEGORIES,
    ARXIV_MAX_RESULTS,
    TOPIC_KEYWORDS,
)

logger.add("logs/download_and_clean.log", rotation="5 MB", retention="7 days")

for d in [RAW_DATA_DIR, RAW_HTML_DIR, RAW_IMAGES_DIR, RAW_PDF_DIR, RAW_JSON_DIR]:
    os.makedirs(d, exist_ok=True)

def save_file(path: str, content, mode="w", binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", encoding=None if binary else "utf-8") as f:
        f.write(content)

def find_matched_keywords(text, keywords):
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]

# NASA APOD: Download JSON and image if relevant
def fetch_nasa_apod(api_key: str, api_url: str, days: int = 1, start_date: str = None):
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        except Exception:
            logger.error("Invalid NASA_APOD_START_DATE format. Use YYYY-MM-DD.")
            start = datetime.today()
    else:
        start = datetime.today()
    for i in range(days):
        date = (start - timedelta(days=i)).strftime("%Y-%m-%d")
        params = {"api_key": api_key, "date": date}
        try:
            resp = requests.get(api_url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            # Save raw JSON
            fname = f"nasa_apod_{date}.json"
            save_file(os.path.join(RAW_JSON_DIR, fname), requests.utils.json.dumps(data, indent=2))
            # Download image if relevant and matches keywords
            combined_text = (data.get("title", "") + " " + data.get("explanation", ""))
            matched_keywords = find_matched_keywords(combined_text, TOPIC_KEYWORDS["Space"])
            if data.get("media_type") == "image" and data.get("url") and matched_keywords:
                img_url = data["url"]
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    ext = img_url.split(".")[-1].split("?")[0]
                    img_fname = f"nasa_apod_{date}.{ext}"
                    save_file(os.path.join(RAW_IMAGES_DIR, img_fname), img_resp.content, binary=True)
                    logger.info(f"Downloaded NASA APOD image to {img_fname}")
        except Exception as e:
            logger.error(f"Exception fetching NASA APOD for {date}: {e}")

# Wikipedia: Download HTML for each keyword topic
def crawl_wikipedia_keywords(topic_keywords, depth=1, max_pages=50, user_agent="ScienceSageBot/1.0"):
    wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)
    seen = set()
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if len(seen) >= max_pages:
                break
            if keyword in seen:
                continue
            page = wiki.page(keyword)
            if not page.exists():
                logger.warning(f"Wikipedia page does not exist: {keyword}")
                continue
            # Download and save the raw HTML of the Wikipedia page
            try:
                html_url = f"https://en.wikipedia.org/api/rest_v1/page/html/{keyword.replace(' ', '_')}"
                resp = requests.get(html_url, headers={"User-Agent": user_agent}, timeout=20)
                if resp.status_code == 200:
                    html_fname = f"wikipedia_{keyword.replace(' ', '_')}.html"
                    save_file(os.path.join(RAW_HTML_DIR, html_fname), resp.text)
                    logger.info(f"Saved Wikipedia HTML to {html_fname}")
                else:
                    logger.warning(f"Failed to fetch HTML for {keyword}: {resp.status_code}")
            except Exception as e:
                logger.error(f"Exception fetching Wikipedia HTML for {keyword}: {e}")
            seen.add(keyword)

# arXiv: Download API XML and PDFs
def fetch_arxiv_papers(categories, max_results=10):
    base_url = "http://export.arxiv.org/api/query"
    for cat in categories:
        logger.info(f"Fetching arXiv papers for category: {cat}")
        params = {
            "search_query": f"cat:{cat}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        try:
            resp = requests.get(base_url, params=params, timeout=20)
            resp.raise_for_status()
            xml_fname = f"arxiv_{cat}.xml"
            save_file(os.path.join(RAW_DATA_DIR, xml_fname), resp.text)
            # Parse XML to get arXiv IDs and download PDFs
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                try:
                    pdf_resp = requests.get(pdf_url, timeout=30)
                    if pdf_resp.status_code == 200:
                        pdf_fname = f"arxiv_{arxiv_id}.pdf"
                        save_file(os.path.join(RAW_PDF_DIR, pdf_fname), pdf_resp.content, binary=True)
                        logger.info(f"Saved arXiv PDF to {pdf_fname}")
                    else:
                        logger.warning(f"Failed to fetch PDF for {arxiv_id}: {pdf_resp.status_code}")
                except Exception as e:
                    logger.error(f"Exception fetching arXiv PDF for {arxiv_id}: {e}")
        except Exception as e:
            logger.error(f"Exception fetching arXiv for {cat}: {e}")

if __name__ == "__main__":
    fetch_nasa_apod(
        NASA_API_KEY,
        NASA_APOD_API_URL,
        days=NASA_APOD_DAYS,
        start_date=NASA_APOD_START_DATE
    )
    crawl_wikipedia_keywords(
        TOPIC_KEYWORDS,
        depth=WIKI_CRAWL_DEPTH,
        max_pages=WIKI_MAX_PAGES,
        user_agent=WIKI_USER_AGENT
    )
    fetch_arxiv_papers(ARXIV_CATEGORIES, max_results=ARXIV_MAX_RESULTS)
import os
import json
import requests
import wikipediaapi
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta

from sciencesage.config import (
    RAW_DATA_DIR,
    RAW_HTML_DIR,
    RAW_IMAGES_DIR,
    RAW_PDF_DIR,
    PROCESSED_DATA_DIR,
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

for d in [RAW_DATA_DIR, RAW_HTML_DIR, RAW_IMAGES_DIR, RAW_PDF_DIR, PROCESSED_DATA_DIR]:
    os.makedirs(d, exist_ok=True)

def save_file(path: str, content, mode="w", binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", encoding=None if binary else "utf-8") as f:
        f.write(content)

def save_standardized_json(data, filename):
    path = os.path.join(PROCESSED_DATA_DIR, filename)
    save_file(path, json.dumps(data, indent=2))
    logger.info(f"Saved standardized data to {filename}")

def find_matched_keywords(text, keywords):
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]

# ----------- NASA APOD API -----------

def fetch_nasa_apod(api_key: str, api_url: str, days: int = 1, start_date: str = None):
    logger.info(f"Fetching NASA APOD for {days} day(s) starting from {start_date or 'latest'}")
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
            combined_text = (data.get("title", "") + " " + data.get("explanation", ""))
            matched_keywords = find_matched_keywords(combined_text, TOPIC_KEYWORDS["Space"])
            std = {
                "source": "nasa_apod",
                "title": data.get("title"),
                "text": data.get("explanation"),
                "date": data.get("date"),
                "url": data.get("url"),
                "image_url": data.get("url") if data.get("media_type") == "image" else None,
                "matched_keywords": matched_keywords,
                "metadata": {k: v for k, v in data.items() if k not in ["title", "explanation", "date", "url", "media_type"]}
            }
            fname = f"nasa_apod_{std['date']}.json"
            save_standardized_json(std, fname)
            # Download image if relevant and save to images dir
            if data.get("media_type") == "image" and data.get("url") and matched_keywords:
                img_url = data["url"]
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    ext = img_url.split(".")[-1].split("?")[0]
                    img_fname = f"nasa_apod_{data['date']}.{ext}"
                    save_file(os.path.join(RAW_IMAGES_DIR, img_fname), img_resp.content, binary=True)
                    logger.info(f"Downloaded NASA APOD image to {img_fname}")
        except Exception as e:
            logger.error(f"Exception fetching NASA APOD for {date}: {e}")

# ----------- Wikipedia API (wikipedia-api) -----------

def fetch_and_save_wikipedia_page(page, name, topic=None, matched_keywords=None):
    if not page.exists():
        logger.warning(f"Wikipedia page does not exist: {page.title}")
        return
    text = page.summary + "\n\n" + page.text
    references = list(page.references.keys()) if hasattr(page, "references") else []
    images = list(page.images.keys()) if hasattr(page, "images") else []
    std = {
        "source": "wikipedia",
        "topic": topic,
        "matched_keywords": matched_keywords or [],
        "title": page.title,
        "text": text,
        "date": None,
        "url": page.fullurl,
        "references": references,
        "images": images,
        "image_url": images[0] if images else None,
        "metadata": {}
    }
    fname = f"wikipedia_{name}.json"
    save_standardized_json(std, fname)

    # Download and save the raw HTML of the Wikipedia page
    try:
        html_url = f"https://en.wikipedia.org/api/rest_v1/page/html/{name}"
        resp = requests.get(html_url, headers={"User-Agent": WIKI_USER_AGENT}, timeout=20)
        if resp.status_code == 200:
            html_fname = f"wikipedia_{name}.html"
            save_file(os.path.join(RAW_HTML_DIR, html_fname), resp.text)
            logger.info(f"Saved Wikipedia HTML to {html_fname}")
        else:
            logger.warning(f"Failed to fetch HTML for {name}: {resp.status_code}")
    except Exception as e:
        logger.error(f"Exception fetching Wikipedia HTML for {name}: {e}")

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
            page_text = (page.title or "") + " " + (page.summary or "") + " " + (page.text or "")
            matched_keywords = [kw for kw in keywords if kw.lower() in page_text.lower()]
            fetch_and_save_wikipedia_page(page, keyword.replace(" ", "_"), topic=topic, matched_keywords=matched_keywords)
            seen.add(keyword)
            # Optionally crawl links for each keyword up to depth
            if depth > 1:
                def crawl_links(page, current_depth):
                    if current_depth > depth:
                        return
                    for linked_title in page.links:
                        if len(seen) >= max_pages:
                            break
                        if linked_title in seen:
                            continue
                        linked_page = wiki.page(linked_title)
                        linked_page_text = (linked_page.title or "") + " " + (linked_page.summary or "") + " " + (linked_page.text or "")
                        matched_keywords_linked = [kw for kw in keywords if kw.lower() in linked_page_text.lower()]
                        fetch_and_save_wikipedia_page(linked_page, linked_title.replace(" ", "_"), topic=topic, matched_keywords=matched_keywords_linked)
                        seen.add(linked_title)
                        crawl_links(linked_page, current_depth + 1)
                crawl_links(page, 2)

# ----------- arXiv API -----------

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
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            papers = []
            for entry in root.findall('atom:entry', ns):
                arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                title = entry.find('atom:title', ns).text.strip()
                abstract = entry.find('atom:summary', ns).text.strip()
                submitted_date = entry.find('atom:published', ns).text
                announced_date = entry.find('atom:updated', ns).text
                authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                categories = [c.attrib['term'] for c in entry.findall('atom:category', ns)]
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                link = next((l.attrib['href'] for l in entry.findall('atom:link', ns) if l.attrib.get('type') == 'text/html'), None)
                paper = {
                    "source": "arxiv",
                    "arxiv_id": arxiv_id,
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "submitted_date": submitted_date,
                    "announced_date": announced_date,
                    "categories": categories,
                    "pdf_url": pdf_url,
                    "link": link,
                    "metadata": {}
                }
                papers.append(paper)
                # Download and save the PDF
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
            json_fname = f"arxiv_{cat}.json"
            save_standardized_json(papers, json_fname)
        except Exception as e:
            logger.error(f"Exception fetching arXiv for {cat}: {e}")

# ----------- Main Pipeline -----------

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
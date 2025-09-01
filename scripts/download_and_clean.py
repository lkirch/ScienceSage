import os
import sys
from pathlib import Path
import requests
import trafilatura
import pdfplumber
import re
import html
from loguru import logger

# Ensure project root is in sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, NASA_URLS, WIKI_TITLES #, PDF_TITLEs

logger.add("logs/download_and_clean.log", rotation="5 MB", retention="7 days")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# ----------- Helpers -----------

def save_file(path: str, content: str, mode="w", binary=False):
    """Utility to save text or binary files."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", encoding=None if binary else "utf-8") as f:
        f.write(content)


def light_clean_text(text: str) -> str:
    """Light cleaning: normalize whitespace, remove encoding artifacts."""
    # Unescape HTML entities
    text = html.unescape(text)
    # Remove common encoding artifacts
    text = text.replace("\u200b", "")  # zero-width space
    text = text.replace("\ufeff", "")  # BOM
    text = text.replace("\xa0", " ")   # non-breaking space
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_html_to_text(html_content: str) -> str:
    """Convert HTML to clean text using trafilatura, then light clean."""
    extracted = trafilatura.extract(html_content, include_links=False, include_images=False) or ""
    return light_clean_text(extracted)


# ----------- Wikipedia API -----------

def fetch_wikipedia_article(title: str) -> str:
    """Fetch plain text of a Wikipedia article using the Wikipedia API."""
    logger.info(f"Fetching Wikipedia article: {title}")
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json",
        "redirects": 1,
    }
    headers = {
        "User-Agent": "ScienceSageBot/1.0 (https://github.com/yourusername/ScienceSage; contact@example.com)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        text = page.get("extract", "")
        if not text:
            logger.warning(f"No extract found for Wikipedia article: {title}")
        return light_clean_text(text)
    except Exception as e:
        logger.error(f"Exception fetching Wikipedia article '{title}': {e}")
        return ""


def download_wikipedia_article(title: str, name: str):
    """Download and save a Wikipedia article using the API."""
    text = fetch_wikipedia_article(title)
    if text:
        processed_path = os.path.join(PROCESSED_DATA_DIR, f"{name}.txt")
        save_file(processed_path, text)
        logger.info(f"Saved Wikipedia article '{title}' to {processed_path}")
    else:
        logger.warning(f"Failed to save Wikipedia article '{title}'")


# ----------- NASA (HTML) -----------

def download_webpage(url: str, name: str):
    """Download a webpage and save clean text."""
    logger.info(f"Downloading {url}")
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            logger.warning(f"Failed to fetch {url} (status {r.status_code})")
            return

        raw_path = os.path.join(RAW_DATA_DIR, f"{name}.html")
        save_file(raw_path, r.text)
        logger.debug(f"Saved raw HTML to {raw_path}")

        clean_text = clean_html_to_text(r.text)
        if clean_text:
            processed_path = os.path.join(PROCESSED_DATA_DIR, f"{name}.txt")
            save_file(processed_path, clean_text)
            logger.info(f"Saved cleaned text to {processed_path}")
        else:
            logger.warning(f"No text extracted from {url}")
    except Exception as e:
        logger.error(f"Exception downloading {url}: {e}")


# ----------- PDFs (Stanford, etc.) -----------

def process_pdf(pdf_path: str, name: str):
    """Extract text from a PDF and save it."""
    logger.info(f"Processing PDF {pdf_path}")
    try:
        all_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

        raw_copy = os.path.join(RAW_DATA_DIR, os.path.basename(pdf_path))
        if not os.path.exists(raw_copy):
            os.makedirs(RAW_DATA_DIR, exist_ok=True)
            with open(pdf_path, "rb") as f:
                save_file(raw_copy, f.read(), binary=True)
            logger.debug(f"Copied raw PDF to {raw_copy}")

        processed_path = os.path.join(PROCESSED_DATA_DIR, f"{name}.txt")
        save_file(processed_path, all_text)
        logger.info(f"Saved PDF text to {processed_path}")
    except Exception as e:
        logger.error(f"Exception processing PDF {pdf_path}: {e}")


# ----------- Main Pipeline -----------

if __name__ == "__main__":
    # Download and clean NASA pages
    for name, url in NASA_URLS.items():
        download_webpage(url, name)

    # Download and clean Wikipedia pages using the API
    for name, title in WIKI_TITLES.items():
        download_wikipedia_article(title, name)

    # Process PDFs (e.g., Stanford LLM slides)
    #for name, path in PDF_TITLES.items():
    #    if os.path.exists(path):
    #        process_pdf(path, name)
    #    else:
    #        print(f"⚠️ PDF {path} not found. Please add it first.")

#!/usr/bin/env python3

import os
import requests
import trafilatura
import pdfplumber
import re
import html

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


# ----------- Helpers -----------

def save_file(path: str, content: str, mode="w", binary=False):
    """Utility to save text or binary files."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", encoding=None if binary else "utf-8") as f:
        f.write(content)


def light_clean_text(text: str) -> str:
    """Light cleaning: strip HTML tags, normalize whitespace, remove encoding artifacts."""
    # Remove HTML tags (fallback if trafilatura misses any)
    text = re.sub(r"<[^>]+>", " ", text)
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


# ----------- Wikipedia + NASA (HTML) -----------

def download_webpage(url: str, name: str):
    """Download a webpage and save clean text."""
    print(f"Downloading {url}")
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        print(f"⚠️ Failed to fetch {url} (status {r.status_code})")
        return

    raw_path = os.path.join(RAW_DIR, f"{name}.html")
    save_file(raw_path, r.text)

    clean_text = clean_html_to_text(r.text)
    if clean_text:
        processed_path = os.path.join(PROCESSED_DIR, f"{name}.txt")
        save_file(processed_path, clean_text)
        print(f"✅ Saved cleaned text to {processed_path}")
    else:
        print(f"⚠️ No text extracted from {url}")


# ----------- PDFs (Stanford, etc.) -----------

def process_pdf(pdf_path: str, name: str):
    """Extract text from a PDF and save it."""
    print(f"Processing PDF {pdf_path}")
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    raw_copy = os.path.join(RAW_DIR, os.path.basename(pdf_path))
    if not os.path.exists(raw_copy):
        os.makedirs(RAW_DIR, exist_ok=True)
        # copy raw pdf into raw folder
        with open(pdf_path, "rb") as f:
            save_file(raw_copy, f.read(), binary=True)

    processed_path = os.path.join(PROCESSED_DIR, f"{name}.txt")
    save_file(processed_path, all_text)
    print(f"✅ Saved PDF text to {processed_path}")


# ----------- Main Pipeline -----------

if __name__ == "__main__":
    # NASA Climate Change pages
    nasa_urls = {
        "nasa_overview": "https://climate.nasa.gov/",
        "nasa_evidence": "https://climate.nasa.gov/evidence/",
        "nasa_causes": "https://climate.nasa.gov/causes/",
        "nasa_effects": "https://climate.nasa.gov/effects/",
        "nasa_scientific_consensus": "https://science.nasa.gov/climate-change/scientific-consensus/",
        "nasa_what_is_climate_change": "https://science.nasa.gov/climate-change/what-is-climate-change/",
        "nasa_extreme_weather": "https://science.nasa.gov/climate-change/extreme-weather/",
        "nasa_wildfires": "https://science.nasa.gov/earth/explore/wildfires-and-climate-change/",
        "nasa_faq": "https://science.nasa.gov/climate-change/faq/",
        "nasa_adaptation_mitigation": "https://science.nasa.gov/climate-change/adaptation-mitigation/",
        "nasa_adaptation_mitigation_resources": "https://science.nasa.gov/climate-change/adaptation-mitigation/resources/",
        
    }

    # Wikipedia pages
    wiki_urls = {
        "neuroplasticity": "https://en.wikipedia.org/wiki/Neuroplasticity",
        "transformer_ml": "https://en.wikipedia.org/wiki/Transformer_(machine_learning)",
        "reinforcement_learning": "https://en.wikipedia.org/wiki/Reinforcement_learning",
        "large_language_model": "https://en.wikipedia.org/wiki/Large_language_model",
        "retrieval_augmented_generation": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        "animal_migration": "https://en.wikipedia.org/wiki/Animal_migration",
        "climate_change_adaptation": "https://en.wikipedia.org/wiki/Climate_change_adaptation",
        "climate_change_and_fisheries": "https://en.wikipedia.org/wiki/Climate_change_and_fisheries",
        "climate_change_and_birds": "https://en.wikipedia.org/wiki/Climate_change_and_birds",
        "decline_in_wild_mammal_populations": "https://en.wikipedia.org/wiki/Decline_in_wild_mammal_populations",
    }

    # Download and clean NASA pages
    for name, url in nasa_urls.items():
        download_webpage(url, name)

    # Download and clean Wikipedia pages
    for name, url in wiki_urls.items():
        download_webpage(url, name)

    # Process PDFs (e.g., Stanford LLM slides)
    # pdf_files = {
    #     "stanford_llm_lecture1": "data/raw/stanford_llm_lecture1.pdf",
    #     # Add more as needed
    # }

    # for name, path in pdf_files.items():
    #     if os.path.exists(path):
    #         process_pdf(path, name)
    #     else:
    #         print(f"⚠️ PDF {path} not found. Please add it first.")

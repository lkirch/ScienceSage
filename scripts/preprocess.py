import os
from pathlib import Path
import json
import hashlib
import uuid
import datetime
import re
from typing import List, Dict
from loguru import logger
import tiktoken

from sciencesage.config import (
    RAW_HTML_DIR,
    RAW_PDF_DIR,
    RAW_DATA_DIR,
    CHUNKS_FILE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOPIC_KEYWORDS,
    MAX_TOKENS,
)

import trafilatura
import pdfplumber
import xml.etree.ElementTree as ET

logger.add("logs/preprocess.log", rotation="5 MB", retention="7 days")
logger.info("Started preprocess.py script.")

def extract_urls(text: str) -> List[str]:
    url_pattern = r"https?://[^\s)]+"
    return re.findall(url_pattern, text)

def chunk_text_by_paragraphs(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = []
    word_count = 0
    for para in paragraphs:
        para_words = para.split()
        if word_count + len(para_words) > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            overlap_words = current_chunk[-overlap:] if overlap > 0 else []
            current_chunk = overlap_words + para_words
            word_count = len(current_chunk)
        else:
            current_chunk.extend(para_words)
            word_count += len(para_words)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    logger.debug(
        f"Chunked text into {len(chunks)} chunks (chunk_size={chunk_size}, overlap={overlap})"
    )
    return chunks

def generate_id(text: str, prefix: str) -> str:
    hash_id = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{hash_id}"

def auto_tag_chunk(text: str) -> list:
    tags = []
    lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw.lower() in lower for kw in keywords):
            tags.append(topic)
    return tags or ["Other"]

def num_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def split_chunk_by_tokens(text: str, max_tokens: int = MAX_TOKENS, model: str = "text-embedding-3-small") -> list:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return [text]
    sub_chunks = []
    for i in range(0, len(tokens), max_tokens):
        sub = tokens[i:i+max_tokens]
        sub_chunks.append(enc.decode(sub))
    return sub_chunks

def get_topic_from_keywords(text: str) -> str:
    lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw.lower() in lower for kw in keywords):
            return topic
    return "Other"

def process_html_file(filepath: Path) -> List[Dict]:
    logger.info(f"Processing HTML file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        extracted = trafilatura.extract(html_content, include_comments=False, include_tables=False, output_format="json")
        if not extracted:
            logger.warning(f"No main content extracted from {filepath.name}")
            return []
        extracted_json = json.loads(extracted)
        text = extracted_json.get("text", "")
        title = extracted_json.get("title") or filepath.stem
        url = extracted_json.get("url")
        images = extracted_json.get("images", [])
        image_url = images[0] if images else None
        reference_urls = extracted_json.get("links", []) or extract_urls(text)
        matched_keywords = [kw for kw in sum(TOPIC_KEYWORDS.values(), []) if kw.lower() in text.lower()]
        topic = get_topic_from_keywords(text)
        filename = filepath.stem
        loadtime = datetime.datetime.now(datetime.UTC).isoformat()
        chunks = chunk_text_by_paragraphs(text)
        results = []
        for i, chunk in enumerate(chunks):
            sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
            for j, sub_chunk in enumerate(sub_chunks):
                chunk_id = generate_id(sub_chunk, filename + f"_{i}_{j}")
                chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
                chunk_topics = auto_tag_chunk(sub_chunk)
                results.append(
                    {
                        "id": chunk_id,
                        "uuid": chunk_uuid,
                        "topics": chunk_topics,
                        "topic": topic,
                        "title": title,
                        "url": url,
                        "image_url": image_url,
                        "images": images,
                        "matched_keywords": matched_keywords,
                        "source": filename,
                        "chunk_index": f"{i}_{j}" if len(sub_chunks) > 1 else i,
                        "text": sub_chunk,
                        "reference_urls": reference_urls,
                        "loadtime": loadtime,
                        "raw_type": "html"
                    }
                )
        logger.info(f"Processed {len(results)} chunks from HTML {filepath.name}")
        return results
    except Exception as e:
        logger.error(f"Failed to process HTML file {filepath}: {e}")
        return []

def process_pdf_file(filepath: Path) -> List[Dict]:
    logger.info(f"Processing PDF file: {filepath}")
    try:
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if not text.strip():
            logger.warning(f"No text extracted from {filepath.name}")
            return []
        filename = filepath.stem
        # Try to find matching arXiv XML for metadata
        xml_path = Path(RAW_DATA_DIR) / f"arxiv_{filename.split('_')[1]}.xml" if "arxiv_" in filename else None
        title = filename
        url = None
        pdf_url = None
        authors = []
        categories = []
        submitted_date = None
        announced_date = None
        if xml_path and xml_path.exists():
            try:
                with open(xml_path, "r", encoding="utf-8") as xf:
                    xml_content = xf.read()
                root = ET.fromstring(xml_content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                    if arxiv_id in filename:
                        title = entry.find('atom:title', ns).text.strip()
                        url = next((l.attrib['href'] for l in entry.findall('atom:link', ns) if l.attrib.get('type') == 'text/html'), None)
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                        categories = [c.attrib['term'] for c in entry.findall('atom:category', ns)]
                        submitted_date = entry.find('atom:published', ns).text
                        announced_date = entry.find('atom:updated', ns).text
                        break
            except Exception as e:
                logger.warning(f"Could not parse arXiv XML for {filename}: {e}")
        reference_urls = extract_urls(text)
        matched_keywords = [kw for kw in sum(TOPIC_KEYWORDS.values(), []) if kw.lower() in text.lower()]
        topic = get_topic_from_keywords(text)
        loadtime = datetime.datetime.now(datetime.UTC).isoformat()
        chunks = chunk_text_by_paragraphs(text)
        results = []
        for i, chunk in enumerate(chunks):
            sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
            for j, sub_chunk in enumerate(sub_chunks):
                chunk_id = generate_id(sub_chunk, filename + f"_{i}_{j}")
                chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
                chunk_topics = auto_tag_chunk(sub_chunk)
                results.append(
                    {
                        "id": chunk_id,
                        "uuid": chunk_uuid,
                        "topics": chunk_topics,
                        "topic": topic,
                        "title": title,
                        "url": url,
                        "pdf_url": pdf_url,
                        "authors": authors,
                        "categories": categories,
                        "submitted_date": submitted_date,
                        "announced_date": announced_date,
                        "matched_keywords": matched_keywords,
                        "source": filename,
                        "chunk_index": f"{i}_{j}" if len(sub_chunks) > 1 else i,
                        "text": sub_chunk,
                        "reference_urls": reference_urls,
                        "loadtime": loadtime,
                        "raw_type": "pdf"
                    }
                )
        logger.info(f"Processed {len(results)} chunks from PDF {filepath.name}")
        return results
    except Exception as e:
        logger.error(f"Failed to process PDF file {filepath}: {e}")
        return []

def process_json_file(filepath: Path) -> List[Dict]:
    logger.info(f"Processing JSON file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = []
        loadtime = datetime.datetime.now(datetime.UTC).isoformat()
        records = data if isinstance(data, list) else [data]
        for record in records:
            text = record.get("text") or record.get("abstract") or ""
            if not text.strip():
                continue
            filename = filepath.stem
            reference_urls = record.get("references", []) or extract_urls(text)
            title = record.get("title", filename)
            url = record.get("url")
            image_url = record.get("image_url")
            images = record.get("images", [])
            pdf_url = record.get("pdf_url")
            authors = record.get("authors", [])
            categories = record.get("categories", [])
            matched_keywords = record.get("matched_keywords", [])
            topic = record.get("topic") if "topic" in record else get_topic_from_keywords(text)
            chunks = chunk_text_by_paragraphs(text)
            for i, chunk in enumerate(chunks):
                sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_id = generate_id(sub_chunk, filename + f"_{i}_{j}")
                    chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
                    chunk_topics = auto_tag_chunk(sub_chunk)
                    results.append(
                        {
                            "id": chunk_id,
                            "uuid": chunk_uuid,
                            "topics": chunk_topics,
                            "topic": topic,
                            "title": title,
                            "url": url,
                            "image_url": image_url,
                            "images": images,
                            "pdf_url": pdf_url,
                            "authors": authors,
                            "categories": categories,
                            "matched_keywords": matched_keywords,
                            "source": filename,
                            "chunk_index": f"{i}_{j}" if len(sub_chunks) > 1 else i,
                            "text": sub_chunk,
                            "reference_urls": reference_urls,
                            "loadtime": loadtime,
                            "raw_type": "json"
                        }
                    )
        logger.info(f"Processed {len(results)} chunks from JSON {filepath.name}")
        return results
    except Exception as e:
        logger.error(f"Failed to process JSON file {filepath}: {e}")
        return []

def main():
    all_chunks = []

    # Process HTML files
    html_dir = Path(RAW_HTML_DIR)
    html_files = list(html_dir.glob("*.html"))
    for filepath in html_files:
        logger.info(f"Processing HTML: {filepath.name}")
        try:
            file_chunks = process_html_file(filepath)
            all_chunks.extend(file_chunks)
        except Exception as e:
            logger.error(f"Failed to process HTML {filepath}: {e}")

    # Process PDF files
    pdf_dir = Path(RAW_PDF_DIR)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    for filepath in pdf_files:
        logger.info(f"Processing PDF: {filepath.name}")
        try:
            file_chunks = process_pdf_file(filepath)
            all_chunks.extend(file_chunks)
        except Exception as e:
            logger.error(f"Failed to process PDF {filepath}: {e}")

    # Process JSON files (for NASA APOD and any other JSON sources)
    raw_data_dir = Path(RAW_DATA_DIR)
    json_files = list(raw_data_dir.glob("*.json"))
    for filepath in json_files:
        logger.info(f"Processing JSON: {filepath.name}")
        try:
            file_chunks = process_json_file(filepath)
            all_chunks.extend(file_chunks)
        except Exception as e:
            logger.error(f"Failed to process JSON {filepath}: {e}")

    try:
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            for entry in all_chunks:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.success(f"Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save chunks to {CHUNKS_FILE}: {e}")

    print(f"✅ Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")

if __name__ == "__main__":
    main()
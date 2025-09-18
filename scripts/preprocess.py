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
    EMBEDDING_MODEL,
    WIKI_URL,
    STANDARD_CHUNK_FIELDS, 
)

import trafilatura
import pdfplumber
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

logger.add("logs/preprocess.log", rotation="5 MB", retention="7 days")
logger.info("Started preprocess.py script.")

def extract_urls(text: str) -> List[str]:
    url_pattern = r"https?://[^\s)]+"
    return re.findall(url_pattern, text)

def extract_reference_urls_from_html(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    refs = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("http"):
            refs.append(href)
        elif href.startswith("/wiki/"):
            refs.append(WIKI_URL + href)
    return list(set(refs))

def extract_images_from_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    imgs = []
    for i, tag in enumerate(soup.find_all("img")):
        src = tag.get("src") or tag.get("data-src")
        if not src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = WIKI_URL + src
        caption = tag.get("alt") or ""
        parent = tag.find_parent(["figure", "div"])
        if parent:
            cap = parent.find("figcaption")
            if cap:
                caption = cap.get_text(strip=True)
        imgs.append({"src": src, "caption": caption})
    return imgs

def extract_tables_from_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    tables = []
    for i, tbl in enumerate(soup.find_all("table")):
        rows = []
        for tr in tbl.find_all("tr"):
            cols = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
            if cols:
                rows.append(cols)
        caption = ""
        cap_tag = tbl.find("caption")
        if cap_tag:
            caption = cap_tag.get_text(strip=True)
        if rows:
            tables.append({"rows": rows, "caption": caption})
    return tables

def insert_placeholders(text: str, images: List[Dict], tables: List[Dict]):
    for i, img in enumerate(images):
        text += f"\n[FIGURE_{i}: {img['caption']}]"
    for i, tbl in enumerate(tables):
        text += f"\n[TABLE_{i}: {tbl['caption']}]"
    return text

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

def num_tokens(text: str, model: str = None) -> int:
    import tiktoken
    model = model or EMBEDDING_MODEL
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def split_chunk_by_tokens(text: str, max_tokens: int = MAX_TOKENS, model: str = None) -> list:
    import tiktoken
    model = model or EMBEDDING_MODEL
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

def make_standard_chunk(**kwargs):
    """Return a dict with all standard fields, filling missing ones with None or sensible defaults."""
    chunk = {}
    for field in STANDARD_CHUNK_FIELDS:
        if field in kwargs:
            chunk[field] = kwargs[field]
        else:
            if field in ("images", "tables", "authors", "topics", "matched_keywords", "reference_urls"):
                chunk[field] = []
            elif field == "embedding_cached":
                chunk[field] = False
            elif field == "chunk_index":
                chunk[field] = 0
            elif field == "char_start":
                chunk[field] = 0
            elif field == "char_end":
                chunk[field] = 0
            else:
                chunk[field] = None
    return chunk

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
        images = extract_images_from_html(html_content)
        tables = extract_tables_from_html(html_content)
        reference_urls = extracted_json.get("links", []) or extract_reference_urls_from_html(html_content)
        matched_keywords = [kw for kw in sum(TOPIC_KEYWORDS.values(), []) if kw.lower() in text.lower()]
        topic = get_topic_from_keywords(text)
        filename = filepath.stem
        loadtime = datetime.datetime.now(datetime.UTC).isoformat()
        text_with_placeholders = insert_placeholders(text, images, tables)
        chunks = chunk_text_by_paragraphs(text_with_placeholders)
        results = []
        char_offset = 0
        section = None
        anchor = None
        published = extracted_json.get("date")
        authors = extracted_json.get("author", [])
        latex = None
        abstract = extracted_json.get("description") or None  # Try to get a summary/lead if available
        for i, chunk in enumerate(chunks):
            sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
            for j, sub_chunk in enumerate(sub_chunks):
                chunk_id = generate_id(sub_chunk, filename + f"_{i}_{j}")
                chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
                chunk_topics = auto_tag_chunk(sub_chunk)
                char_start = char_offset
                char_end = char_offset + len(sub_chunk)
                char_offset = char_end
                results.append(
                    make_standard_chunk(
                        id=chunk_id,
                        uuid=chunk_uuid,
                        text=sub_chunk,
                        source="wikipedia" if "wikipedia" in filename else "html",
                        title=title,
                        url=url,
                        doc_id=filename,
                        page=None,
                        section=section,
                        anchor=anchor,
                        chunk_index=i,
                        char_start=char_start,
                        char_end=char_end,
                        images=[img["src"] for img in images],
                        tables=[f"data/raw/tables/{filename}_table{i}.csv" for i in range(len(tables))],
                        latex=latex,
                        published=published,
                        authors=authors if isinstance(authors, list) else [authors],
                        topics=chunk_topics,
                        topic=topic,
                        matched_keywords=matched_keywords,
                        reference_urls=reference_urls,
                        loadtime=loadtime,
                        raw_type="html",
                        level="unknown",
                        abstract=abstract,
                    )
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
        xml_path = Path(RAW_DATA_DIR) / f"arxiv_{filename.split('_')[1]}.xml" if "arxiv_" in filename else None
        title = filename
        url = None
        pdf_url = None
        authors = []
        categories = []
        submitted_date = None
        announced_date = None
        published = None
        doc_id = filename
        abstract = None
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
                        published = submitted_date
                        doc_id = arxiv_id
                        abstract = entry.find('atom:summary', ns).text.strip()
                        break
            except Exception as e:
                logger.warning(f"Could not parse arXiv XML for {filename}: {e}")
        reference_urls = extract_urls(text)
        matched_keywords = [kw for kw in sum(TOPIC_KEYWORDS.values(), []) if kw.lower() in text.lower()]
        topic = get_topic_from_keywords(text)
        loadtime = datetime.datetime.now(datetime.UTC).isoformat()
        results = []
        char_offset = 0
        latex = None
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            chunks = chunk_text_by_paragraphs(page_text)
            for i, chunk in enumerate(chunks):
                sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_id = generate_id(sub_chunk, filename + f"_{page_num}_{i}_{j}")
                    chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
                    chunk_topics = auto_tag_chunk(sub_chunk)
                    char_start = char_offset
                    char_end = char_offset + len(sub_chunk)
                    char_offset = char_end
                    results.append(
                        make_standard_chunk(
                            id=chunk_id,
                            uuid=chunk_uuid,
                            text=sub_chunk,
                            source="arxiv" if "arxiv" in filename else "pdf",
                            title=title,
                            url=url,
                            doc_id=doc_id,
                            page=page_num + 1,
                            section=None,
                            anchor=None,
                            chunk_index=i,
                            char_start=char_start,
                            char_end=char_end,
                            images=[],
                            tables=[],
                            latex=latex,
                            published=published,
                            authors=authors,
                            topics=chunk_topics,
                            topic=topic,
                            matched_keywords=matched_keywords,
                            reference_urls=reference_urls,
                            loadtime=loadtime,
                            raw_type="pdf",
                            level="unknown",
                            abstract=abstract,
                        )
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
            published = record.get("published")
            doc_id = record.get("doc_id", filename)
            latex = record.get("latex")
            section = record.get("section")
            anchor = record.get("anchor")
            abstract = record.get("abstract")
            chunks = chunk_text_by_paragraphs(text)
            char_offset = 0
            for i, chunk in enumerate(chunks):
                sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_id = generate_id(sub_chunk, filename + f"_{i}_{j}")
                    chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
                    chunk_topics = auto_tag_chunk(sub_chunk)
                    char_start = char_offset
                    char_end = char_offset + len(sub_chunk)
                    char_offset = char_end
                    results.append(
                        make_standard_chunk(
                            id=chunk_id,
                            uuid=chunk_uuid,
                            text=sub_chunk,
                            source=record.get("source", "json"),
                            title=title,
                            url=url,
                            doc_id=doc_id,
                            page=record.get("page"),
                            section=section,
                            anchor=anchor,
                            chunk_index=i,
                            char_start=char_start,
                            char_end=char_end,
                            images=images,
                            tables=record.get("tables", []),
                            latex=latex,
                            published=published,
                            authors=authors,
                            topics=chunk_topics,
                            topic=topic,
                            matched_keywords=matched_keywords,
                            reference_urls=reference_urls,
                            loadtime=loadtime,
                            raw_type="json",
                            level="unknown",
                            abstract=abstract,
                        )
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
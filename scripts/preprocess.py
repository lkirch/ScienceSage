from pathlib import Path
import json
import hashlib
import uuid
import datetime
import re
from typing import List, Dict
from loguru import logger

from sciencesage.config import (
    RAW_HTML_DIR,
    RAW_PDF_DIR,
    RAW_DATA_DIR,
    RAW_XML_DIR,
    RAW_JSON_DIR,
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
import fitz  # PyMuPDF
import os
import csv

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
            elif field == "chunk_index":
                chunk[field] = 0
            elif field == "char_start":
                chunk[field] = 0
            elif field == "char_end":
                chunk[field] = 0
            else:
                chunk[field] = None
    return chunk

def remove_wikipedia_refs(text: str) -> str:
    # Remove patterns like [14], [15], [14][15], [a], [citation needed], etc.
    return re.sub(r'\[(?:\d+|[a-zA-Z]+|citation needed)\]', '', text)

def extract_images_from_pdf(filepath: Path, output_dir: Path) -> list:
    """Extract images from PDF using fitz and save them to output_dir. Returns list of image file paths."""
    images = []
    doc = fitz.open(str(filepath))
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"{filepath.stem}_page{page_num+1}_img{img_index+1}.{image_ext}"
            image_path = output_dir / image_name
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            images.append(str(image_path))
    return images

def extract_tables_from_pdf(pdf, output_dir: Path, filename: str) -> list:
    """Extract tables from pdfplumber PDF object and save as CSV. Returns list of CSV file paths."""
    tables = []
    for page_num, page in enumerate(pdf.pages):
        page_tables = page.extract_tables()
        for tbl_idx, table in enumerate(page_tables):
            if not table:
                continue
            csv_name = f"{filename}_page{page_num+1}_table{tbl_idx+1}.csv"
            csv_path = output_dir / csv_name
            with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                for row in table:
                    writer.writerow(row)
            tables.append(str(csv_path))
    return tables

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
        text = remove_wikipedia_refs(text)  # Clean Wikipedia reference markers
        title = extracted_json.get("title") or filepath.stem

        # --- Get URL from meta.json if it exists ---
        meta_path = filepath.with_suffix(filepath.suffix + ".meta.json")
        url = None
        if meta_path.exists():
            with open(meta_path, "r") as f:
                meta = json.load(f)
            url = meta.get("url")
        else:
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
        authors = extracted_json.get("author", [])
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
                        chunk_index=i,
                        char_start=char_start,
                        char_end=char_end,
                        images=[img["src"] for img in images],
                        tables=[f"data/raw/tables/{filename}_table{i}.csv" for i in range(len(tables))],
                        authors=authors if isinstance(authors, list) else [authors],
                        topics=chunk_topics,
                        topic=topic,
                        matched_keywords=matched_keywords,
                        reference_urls=reference_urls,
                        loadtime=loadtime,
                        raw_type="html",
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
        # --- Extract images using fitz ---
        images_dir = Path(RAW_DATA_DIR) / "pdf_images"
        images_dir.mkdir(parents=True, exist_ok=True)
        images = extract_images_from_pdf(filepath, images_dir)

        # --- Extract tables using pdfplumber ---
        tables_dir = Path(RAW_DATA_DIR) / "tables"
        tables_dir.mkdir(parents=True, exist_ok=True)
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            tables = extract_tables_from_pdf(pdf, tables_dir, filepath.stem)

        if not text.strip():
            logger.warning(f"No text extracted from {filepath.name}")
            return []
        filename = filepath.stem
        # --- Find the matching XML file in RAW_XML_DIR ---
        arxiv_id = None
        if filename.startswith("arxiv_"):
            arxiv_id = filename.replace("arxiv_", "")
        xml_path = None
        if arxiv_id:
            for xml_file in Path(RAW_XML_DIR).glob("arxiv_*.xml"):
                with open(xml_file, "r", encoding="utf-8") as xf:
                    xml_content = xf.read()
                root = ET.fromstring(xml_content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    entry_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                    if arxiv_id in entry_id:
                        xml_path = xml_file
                        break
                if xml_path:
                    break

        title = filename
        url = None
        pdf_url = None
        authors = []
        categories = []
        doc_id = filename
        abstract = None
        if xml_path and xml_path.exists():
            try:
                with open(xml_path, "r", encoding="utf-8") as xf:
                    xml_content = xf.read()
                root = ET.fromstring(xml_content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    entry_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                    if arxiv_id and arxiv_id in entry_id:
                        title = entry.find('atom:title', ns).text.strip()
                        url = entry.find('atom:id', ns).text
                        pdf_url = f"https://arxiv.org/pdf/{entry_id}.pdf"
                        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                        if not authors:
                            author_field = entry.find('atom:author', ns)
                            if author_field is not None and author_field.text:
                                authors = [author_field.text.strip()]
                        categories = [c.attrib['term'] for c in entry.findall('atom:category', ns)]
                        doc_id = entry_id
                        summary_elem = entry.find('atom:summary', ns)
                        if summary_elem is not None and summary_elem.text:
                            abstract = summary_elem.text.strip()
                        else:
                            abstract_elem = entry.find('atom:abstract', ns)
                            if abstract_elem is not None and abstract_elem.text:
                                abstract = abstract_elem.text.strip()
                        break
            except Exception as e:
                logger.warning(f"Could not parse arXiv XML for {filename}: {e}")
        reference_urls = extract_urls(text)
        matched_keywords = [kw for kw in sum(TOPIC_KEYWORDS.values(), []) if kw.lower() in text.lower()]
        topic = get_topic_from_keywords(text)
        loadtime = datetime.datetime.now(datetime.UTC).isoformat()
        results = []
        char_offset = 0
        with pdfplumber.open(filepath) as pdf:
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
                                chunk_index=i,
                                char_start=char_start,
                                char_end=char_end,
                                images=images,
                                tables=tables,
                                authors=authors,
                                topics=chunk_topics,
                                topic=topic,
                                matched_keywords=matched_keywords,
                                reference_urls=reference_urls,
                                loadtime=loadtime,
                                raw_type="pdf",
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
        # Handle NASA APOD JSON structure (copyright is optional)
        if (
            "title" in data
            and "explanation" in data
            and "url" in data
            and "hdurl" in data
        ):
            title = data.get("title")
            text = data.get("explanation")
            url = data.get("url")
            abstract = data.get("explanation")
            reference_urls = [data.get("hdurl")]
            # Copyright is optional
            copyright_val = data.get("copyright")
            authors = [copyright_val] if copyright_val else []
            doc_id = filepath.stem
            loadtime = datetime.datetime.now(datetime.UTC).isoformat()
            matched_keywords = [kw for kw in sum(TOPIC_KEYWORDS.values(), []) if kw.lower() in text.lower()]
            topic = get_topic_from_keywords(text)
            chunks = chunk_text_by_paragraphs(text)
            # Ensure at least one chunk
            if not chunks:
                chunks = [text]
            results = []
            char_offset = 0
            for i, chunk in enumerate(chunks):
                sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
                # Ensure at least one sub_chunk
                if not sub_chunks:
                    sub_chunks = [chunk]
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_id = generate_id(sub_chunk, doc_id + f"_{i}_{j}")
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
                            source="nasa",
                            title=title,
                            url=url,
                            doc_id=doc_id,
                            page=None,
                            chunk_index=i,
                            char_start=char_start,
                            char_end=char_end,
                            images=[],
                            tables=[],
                            authors=authors,
                            topics=chunk_topics,
                            topic=topic,
                            matched_keywords=matched_keywords,
                            reference_urls=reference_urls,
                            loadtime=loadtime,
                            raw_type="json",
                            abstract=abstract,
                        )
                    )
            logger.info(f"Processed {len(results)} chunks from NASA APOD JSON {filepath.name}")
            return results
        else:
            logger.warning(f"JSON structure not recognized for {filepath.name}")
            return []
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
    raw_data_dir = Path(RAW_JSON_DIR)
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
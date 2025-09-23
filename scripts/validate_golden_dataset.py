import json
from collections import Counter
from pathlib import Path
from loguru import logger

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from sciencesage.config import GOLDEN_DATA_FILE, CHUNKS_FILE

REQUIRED_FIELDS = ["query", "expected_answer", "context_ids", "difficulty_level", "metadata"]
ALLOWED_DIFFICULTY = {"middle_school", "college", "advanced"}

def validate_line(obj, idx, seen_queries, valid_context_ids):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in obj:
            errors.append(f"Missing field: {field}")
    if not isinstance(obj.get("context_ids", []), list) or not obj.get("context_ids"):
        errors.append("context_ids must be a non-empty list")
    else:
        if valid_context_ids is not None:
            for cid in obj["context_ids"]:
                if cid not in valid_context_ids:
                    errors.append(f"context_id '{cid}' not found in chunks")
    if obj.get("difficulty_level") not in ALLOWED_DIFFICULTY:
        errors.append(f"Invalid difficulty_level: {obj.get('difficulty_level')}")
    if not obj.get("query"):
        errors.append("Empty query")
    if not obj.get("expected_answer"):
        errors.append("Empty expected_answer")
    if not isinstance(obj.get("metadata", {}), dict) or "topic" not in obj.get("metadata", {}):
        errors.append("metadata must be a dict with a 'topic' key")
    query = obj.get("query", "").strip().lower()
    if query:
        seen_queries[query] += 1
    if errors:
        logger.error(f"Line {idx+1}: {'; '.join(errors)}")

def load_valid_context_ids(chunks_path=CHUNKS_FILE):
    valid_ids = set()
    try:
        with open(chunks_path) as f:
            for line in f:
                try:
                    chunk = json.loads(line)
                    if "id" in chunk:
                        valid_ids.add(chunk["id"])
                except Exception:
                    continue
    except FileNotFoundError:
        logger.warning(f"Chunks file not found: {chunks_path}")
        return None
    return valid_ids if valid_ids else None

def main():
    logger.add("logs/validate_golden_dataset.log", rotation="1 MB", retention="7 days")
    seen_queries = Counter()
    valid_context_ids = load_valid_context_ids()
    total = 0
    golden_data_path = Path(GOLDEN_DATA_FILE)
    if not golden_data_path.exists():
        logger.error(f"Golden dataset file not found: {golden_data_path}")
        return
    with open(golden_data_path) as f:
        for idx, line in enumerate(f):
            try:
                obj = json.loads(line)
                validate_line(obj, idx, seen_queries, valid_context_ids)
                total += 1
            except Exception as e:
                logger.error(f"Line {idx+1}: Invalid JSON ({e})")
    dups = [q for q, count in seen_queries.items() if count > 1]
    if dups:
        logger.warning(f"Duplicate queries found ({len(dups)}):")
        for q in dups:
            logger.warning(f"  '{q}' appears {seen_queries[q]} times")
    logger.success(f"Validation complete. Checked {total} lines.")

if __name__ == "__main__":
    main()
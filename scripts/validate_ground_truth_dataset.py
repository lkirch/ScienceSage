import json
from collections import Counter
from pathlib import Path

from sciencesage.config import GROUND_TRUTH_FILE, LEVELS, logger   

REQUIRED_FIELDS = ["chunk_id", "topic", "text", "level", "question", "answer", "ground_truth_chunks"]

def validate_line(obj, idx, seen_questions):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in obj:
            errors.append(f"Missing field: {field}")
    if obj.get("level") not in LEVELS:
        errors.append(f"Invalid level: {obj.get('level')}")
    if not obj.get("question"):
        errors.append("Empty question")
    if not obj.get("answer"):
        errors.append("Empty answer")
    question = obj.get("question", "").strip().lower()
    if question:
        seen_questions[question] += 1
    if errors:
        logger.error(f"Line {idx+1}: {'; '.join(errors)}")

def main():
    seen_questions = Counter()
    total = 0
    ground_truth_path = Path(GROUND_TRUTH_FILE)
    if not ground_truth_path.exists():
        logger.error(f"Ground truth dataset file not found: {ground_truth_path}")
        return
    with open(ground_truth_path) as f:
        for idx, line in enumerate(f):
            try:
                obj = json.loads(line)
                validate_line(obj, idx, seen_questions)
                total += 1
            except Exception as e:
                logger.error(f"Line {idx+1}: Invalid JSON ({e})")
    dups = [q for q, count in seen_questions.items() if count > 1]
    if dups:
        logger.warning(f"Duplicate queries found ({len(dups)}):")
        for q in dups:
            logger.warning(f"  '{q}' appears {seen_questions[q]} times")
    logger.success(f"Validation complete. Checked {total} lines.")

if __name__ == "__main__":
    main()
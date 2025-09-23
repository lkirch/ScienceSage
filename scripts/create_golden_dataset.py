import json
import random
import sys
import re
from pathlib import Path
from openai import OpenAI
from loguru import logger
from tqdm import tqdm
import time

# Ensure project root is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from sciencesage.config import CHUNKS_FILE, GOLDEN_DATA_FILE, OPENAI_API_KEY, CHAT_MODEL, TOPICS

logger.add("logs/create_golden_dataset.log", rotation="5 MB", retention="7 days")

client = OpenAI(api_key=OPENAI_API_KEY)

NUM_EXAMPLES = 80
MAX_QUESTIONS_PER_CHUNK = 2

SYSTEM_PROMPT = """You are a helpful assistant creating a golden evaluation dataset for a RAG LLM system.
Given a passage, generate up to 2 diverse Q&A pairs that can be answered using the passage.
- Include a mix of 'middle_school', 'college', and 'advanced' questions.
- Keep questions grounded and factually answerable from the text.
- Answers must be concise but factually correct.
- Return as a JSON list with fields: query, expected_answer, difficulty_level.
"""

def load_chunks():
    chunks = []
    with open(CHUNKS_FILE, "r") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def extract_json_from_codeblock(content):
    """
    Extract JSON from a markdown code block if present.
    """
    # Remove leading/trailing whitespace
    content = content.strip()
    # Remove triple backticks and optional 'json' after them
    if content.startswith("```"):
        # Remove the first line (```json or ```)
        lines = content.splitlines()
        # Remove the first and last line (the code block markers)
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            return "\n".join(lines[1:-1])
    return content

def generate_questions(chunk_text):
    prompt = f"Passage:\n{chunk_text}\n\nGenerate Q&A pairs as requested."
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        logger.error("OpenAI response was empty.")
        return []
    try:
        json_content = extract_json_from_codeblock(content)
        return json.loads(json_content)
    except Exception as e:
        logger.error(f"Failed to parse response: {e}\nRaw response: {content}")
        return []

def main():
    chunks = load_chunks()
    logger.info(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    sampled_chunks = random.sample(chunks, min(len(chunks), NUM_EXAMPLES))
    results = []

    start_time = time.time()
    for idx, c in enumerate(tqdm(sampled_chunks, desc="Generating Q&A")):
        logger.info(f"Processing chunk {idx+1}/{len(sampled_chunks)} (id={c.get('id', f'chunk_{idx}')})")
        qas = generate_questions(c["text"])
        chunk_id = c.get("id", f"chunk_{idx}")
        topic = c.get("topic") or c.get("title") or TOPICS[idx % len(TOPICS)]
        for qa in qas[:MAX_QUESTIONS_PER_CHUNK]:
            results.append({
                "query": qa["query"],
                "expected_answer": qa["expected_answer"],
                "context_ids": [chunk_id],
                "difficulty_level": qa.get("difficulty_level", "middle_school"),
                "metadata": {"topic": topic}
            })
    elapsed = time.time() - start_time

    # Ensure the parent directory exists
    golden_data_path = Path(GOLDEN_DATA_FILE)
    golden_data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(golden_data_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    logger.success(f"Golden dataset created with {len(results)} examples at {GOLDEN_DATA_FILE}")
    logger.info(f"Elapsed time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()

import json
import random
from pathlib import Path
from loguru import logger
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from openai import OpenAI, RateLimitError

from sciencesage.config import CHUNKS_FILE, GROUND_TRUTH_FILE, TOPICS, EMBEDDING_MODEL, LEVELS, CHAT_MODEL, MAX_TOKENS  

logger.add("logs/create_ground_truth_dataset.log", rotation="5 MB", retention="7 days")

NUM_EXAMPLES = 80
TEMPERATURE = 0.3

SYSTEM_PROMPT = """You are a helpful assistant creating a ground truth evaluation dataset for a RAG LLM system.
Given a chunk, generate up to 3 diverse Q&A pairs that can be answered using that chunk.
- Only generate answers that are explicitly stated or can be directly inferred from the chunk.
- Include a question at each level: 'Middle School', 'College', and 'Advanced'.
- Keep questions grounded and factually answerable from the text.
- Do not use outside knowledge.
- Answers must be concise but factually correct.
- Return as a JSON list with fields: query, expected_answer, difficulty_level.
"""

client = OpenAI()

def load_chunks():
    chunks = []
    with open(CHUNKS_FILE, "r") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def extract_json_from_codeblock(content):
    # Extract JSON from code block if present
    import re
    match = re.search(r"```json(.*?)```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()    

def generate_questions_by_level(chunk: str) -> dict:
    """
    Calls GPT to generate up to 3 diverse Q&A pairs from the chunk.
    Returns a dictionary keyed by level: {"Middle School": {...}, "College": {...}, "Advanced": {...}}
    """
    from sciencesage.config import LEVELS  
    
    prompt = SYSTEM_PROMPT + f"\nChunk:\n{chunk}\n\nGenerate questions now."

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,  #            
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": chunk}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        content = response.choices[0].message.content
        logger.debug(f"Raw OpenAI response: {content}")
        json_str = extract_json_from_codeblock(content)

        qa_list = json.loads(json_str)

        result = {}
        for qa in qa_list:
            logger.debug(f"Returned difficulty_level: {qa.get('difficulty_level')}")
            level = qa.get("difficulty_level", "").lower()
            # Normalize level to match your LEVELS list
            if level not in [lvl.lower() for lvl in LEVELS]:
                logger.warning(f"Skipping QA with invalid difficulty_level: {level}")
                continue
            result[level] = {
                "query": qa.get("query"),
                "expected_answer": qa.get("expected_answer"),
                "difficulty_level": level
            }
        return result

    except RateLimitError as e:
        logger.error(f"OpenAI rate limit error: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to generate Q&A for passage: {e}")
        return {}


def group_chunks_by_topic(chunks):
    from collections import defaultdict
    topic_map = defaultdict(list)
    for c in chunks:
        topic = c.get("topic", "other")
        topic_map[topic].append(c)
    return topic_map

def main():
    chunks = load_chunks()
    logger.info(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info(f"Loaded embedding model: {EMBEDDING_MODEL}")

    # Guarantee at least one group of 3 Q&A for each topic
    topic_map = group_chunks_by_topic(chunks)
    results = []

    for topic, topic_chunks in topic_map.items():
        # Sample one chunk per topic (or use all if <1)
        sampled = random.sample(topic_chunks, 1) if len(topic_chunks) > 0 else []
        for c in sampled:
            chunk_id = c.get("uuid", "topic_" + topic)
            text = c["text"]
            qa_pairs_by_level = generate_questions_by_level(text)
            for level in LEVELS:
                qa = qa_pairs_by_level.get(level.lower())
                if qa:
                    results.append({
                        "chunk_id": chunk_id,
                        "topic": topic,
                        "text": text,
                        "level": qa.get("difficulty_level", level),
                        "question": qa["query"],
                        "answer": qa["expected_answer"]
                    })

    # Then sample the rest as before, but avoid duplicating the topic chunks already used
    used_chunk_ids = {r["chunk_id"] for r in results}
    remaining_chunks = [c for c in chunks if c.get("uuid", None) not in used_chunk_ids]
    sampled_chunks = random.sample(remaining_chunks, min(len(remaining_chunks), NUM_EXAMPLES))

    for idx, c in enumerate(tqdm(sampled_chunks, desc="Generating ground truth")):
        chunk_id = c.get("uuid", str(idx))
        topic = c.get("topic") or c.get("title") or TOPICS[idx % len(TOPICS)]
        text = c["text"]

        qa_pairs_by_level = generate_questions_by_level(text)
        for level in LEVELS:
            qa = qa_pairs_by_level.get(level.lower())
            if qa:
                results.append({
                    "chunk_id": chunk_id,
                    "topic": topic,
                    "text": text,
                    "level": qa.get("difficulty_level", level),
                    "question": qa["query"],
                    "answer": qa["expected_answer"]
                })

    ground_truth_path = Path(GROUND_TRUTH_FILE)
    ground_truth_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ground_truth_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    logger.success(f"Ground truth dataset created with {len(results)} examples at {ground_truth_path}")

if __name__ == "__main__":
    main()

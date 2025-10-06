import numpy as np

def normalize_text(text):
    """Lowercase and strip extra spaces."""
    return text.strip().lower() if isinstance(text, str) else ""

def safe_list(texts):
    """Ensure the input is a clean list of strings."""
    if not texts:
        return []
    return [normalize_text(t) for t in texts if isinstance(t, str) and t.strip()]

def match(chunk, relevant_set):
    """Check if two text chunks roughly match using substring overlap."""
    return any(chunk in r or r in chunk for r in relevant_set)

def precision_at_k(retrieved_texts, relevant_texts, k):
    retrieved_texts = safe_list(retrieved_texts)
    relevant_texts = safe_list(relevant_texts)
    retrieved_k = retrieved_texts[:k]
    relevant_set = set(relevant_texts)
    if not retrieved_k or not relevant_set or k == 0:
        return 0.0
    return len([chunk for chunk in retrieved_k if match(chunk, relevant_set)]) / k

def recall_at_k(retrieved_texts, relevant_texts, k):
    retrieved_texts = safe_list(retrieved_texts)
    relevant_texts = safe_list(relevant_texts)
    retrieved_k = retrieved_texts[:k]
    relevant_set = set(relevant_texts)
    if not relevant_set:
        return 0.0
    return len([chunk for chunk in retrieved_k if match(chunk, relevant_set)]) / len(relevant_set)

def reciprocal_rank(retrieved_texts, relevant_texts):
    retrieved_texts = safe_list(retrieved_texts)
    relevant_texts = safe_list(relevant_texts)
    relevant_set = set(relevant_texts)
    for idx, chunk in enumerate(retrieved_texts, 1):
        if match(chunk, relevant_set):
            return 1.0 / idx
    return 0.0

def dcg(retrieved_texts, relevant_texts, k):
    retrieved_texts = safe_list(retrieved_texts)
    relevant_texts = safe_list(relevant_texts)
    relevant_set = set(relevant_texts)
    dcg_val = 0.0
    for i, chunk in enumerate(retrieved_texts[:k]):
        rel = 1 if match(chunk, relevant_set) else 0
        dcg_val += rel / np.log2(i + 2)
    return dcg_val

def ndcg_at_k(retrieved_texts, relevant_texts, k):
    retrieved_texts = safe_list(retrieved_texts)
    relevant_texts = safe_list(relevant_texts)
    if not relevant_texts:
        return 0.0
    ideal_rels = [1] * min(len(relevant_texts), k)
    ideal_dcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_rels))
    if ideal_dcg == 0:
        return 0.0
    return dcg(retrieved_texts, relevant_texts, k) / ideal_dcg

def contextual_recall_and_sufficiency(retrieved_texts, relevant_texts, k):
    """Placeholder for semantic sufficiency — reuse recall for now."""
    return recall_at_k(retrieved_texts, relevant_texts, k)
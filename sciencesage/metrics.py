import numpy as np

def normalize_text(text):
    return text.strip().lower() if isinstance(text, str) else text

def precision_at_k(retrieved_texts, relevant_texts, k):
    retrieved_k = [normalize_text(x) for x in retrieved_texts[:k]]
    relevant_set = set(normalize_text(x) for x in relevant_texts)
    return len([chunk for chunk in retrieved_k if chunk in relevant_set]) / k if k else 0.0

def recall_at_k(retrieved_texts, relevant_texts, k):
    retrieved_k = [normalize_text(x) for x in retrieved_texts[:k]]
    relevant_set = set(normalize_text(x) for x in relevant_texts)
    return len([chunk for chunk in retrieved_k if chunk in relevant_set]) / len(relevant_set) if relevant_set else 0.0

def reciprocal_rank(retrieved_texts, relevant_texts):
    relevant_set = set(normalize_text(x) for x in relevant_texts)
    for idx, chunk in enumerate([normalize_text(x) for x in retrieved_texts], 1):
        if chunk in relevant_set:
            return 1.0 / idx
    return 0.0

def dcg(retrieved_texts, relevant_texts, k):
    dcg_val = 0.0
    relevant_set = set(normalize_text(x) for x in relevant_texts)
    for i, chunk in enumerate([normalize_text(x) for x in retrieved_texts[:k]]):
        rel = 1 if chunk in relevant_set else 0
        dcg_val += rel / (np.log2(i + 2))
    return dcg_val

def ndcg_at_k(retrieved_texts, relevant_texts, k):
    ideal_rels = [1] * min(len(relevant_texts), k)
    ideal_dcg = sum([rel / np.log2(i + 2) for i, rel in enumerate(ideal_rels)])
    if ideal_dcg == 0:
        return 0.0
    return dcg(retrieved_texts, relevant_texts, k) / ideal_dcg

def contextual_recall_and_sufficiency(retrieved_texts, relevant_texts, k):
    return recall_at_k(retrieved_texts, relevant_texts, k)
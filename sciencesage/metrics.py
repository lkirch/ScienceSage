import numpy as np

def precision_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)
    return len([chunk for chunk in retrieved_k if chunk in relevant_set]) / k if k else 0.0

def recall_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)
    return len([chunk for chunk in retrieved_k if chunk in relevant_set]) / len(relevant_set) if relevant_set else 0.0

def reciprocal_rank(retrieved, relevant):
    relevant_set = set(relevant)
    for idx, chunk in enumerate(retrieved, 1):
        if chunk in relevant_set:
            return 1.0 / idx
    return 0.0

def dcg(retrieved, relevant, k):
    dcg_val = 0.0
    relevant_set = set(relevant)
    for i, chunk in enumerate(retrieved[:k]):
        rel = 1 if chunk in relevant_set else 0
        dcg_val += rel / (np.log2(i + 2))
    return dcg_val

def ndcg_at_k(retrieved, relevant, k):
    ideal_rels = [1] * min(len(relevant), k)
    ideal_dcg = sum([rel / np.log2(i + 2) for i, rel in enumerate(ideal_rels)])
    if ideal_dcg == 0:
        return 0.0
    return dcg(retrieved, relevant, k) / ideal_dcg

def contextual_recall_and_sufficiency(retrieved, relevant, k):
    # Placeholder: may require human or LLM judgment
    return recall_at_k(retrieved, relevant, k)
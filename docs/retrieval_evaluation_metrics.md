📊 Retrieval Evaluation Metrics Summary

![Retrieval Evaluation Metrics](images/retrieval_evaluation_metrics.png)

*Figure: Visual summary of retrieval evaluation metrics used in ScienceSage. This diagram illustrates how each metric assesses different aspects of retrieval quality, such as accuracy, ranking, and contextual sufficiency.*



 Metric                          | Description                                                         | Formula                                                                    | Range   | Goal                                   |
|--------------------------------|---------------------------------------------------------------------|----------------------------------------------------------------------------|---------|----------------------------------------|
| Precision@K                    | Fraction of top-K retrieved chunks that are relevant.               | Precision@K = (# relevant in top K) / K                                    |  0 – 1  | Higher = more accurate retrievals      |
| Recall@K                       | Fraction of relevant chunks that appear in top-K results.           | Recall@K = (# relevant in top K) / (Total # relevant)                      |  0 – 1  | Higher = more comprehensive retrievals |
| Reciprocal Rank (MRR)          | Inverse of the rank of the first relevant chunk.                    | MRR = 1 / (rank of first relevant result)                                  |  0 – 1  | Higher = relevant results appear earlier|
| nDCG@K                         | Normalized Discounted Cumulative Gain — ranks relevance by position.| nDCG@K = DCG@K / IDCG@K, where DCG = Σ(rel_i / log2(i+2))                  |  0 – 1  | Higher = better ranking order          |
| Contextual Recall / Sufficiency| Recall-based measure for contextual completeness.                   | Same as Recall@K                                                           |  0 – 1  | Higher = covers more ground truth      |
| Semantic Similarity (MiniLM)   | Mean cosine similarity between retrieved and relevant embeddings.   | Mean cosine similarity between retrieved and relevant chunk embeddings     |  0 – 1  | Higher = more semantically aligned     |
| Fuzzy Match Recall             | Recall using fuzzy string matching for minor text differences.      | (# fuzzy matches in top K) / (Total # relevant)                            |  0 – 1  | Higher = robust to text variations     |


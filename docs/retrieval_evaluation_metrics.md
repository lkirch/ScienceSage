📊 Retrieval Evaluation Metrics Summary

<div align="center">
  <img src="../images/retrieval_evaluation_metrics.png" alt="Retrieval Evaluation Metrics" width="400"/>
</div>

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


<div align="center">
  <img src="../images/avg_metrics_w_stddev_error_bars.png" alt="Average Metric Values with Standard Deviation Error Bars for Retrieval and LLM" width="600"/>
</div>

<div align="center">
  <img src="retrieval_vs_llm_mean_metrics.png" alt="Side-by-side comparison of mean metric values for Retrieval and LLMError Bars for Retrieval and LLM" width="600"/>
</div>


## Observations

* **Recall@K** is very high (≈0.88) for both retrieval and LLM, indicating that the system is able to retrieve most of the relevant chunks for each query. This suggests strong coverage of ground truth information.

* **Precision@K** is low (≈0.09), meaning that while many relevant chunks are retrieved, a large proportion of the top-K results are not relevant. This is typical in open-domain retrieval with large context windows and suggests room for improvement in ranking or filtering.

* **Reciprocal Rank** (MRR ≈0.69) and nDCG@K (≈0.74) are moderate, showing that relevant chunks often appear early in the results, but not always at the very top. The ranking is decent but not perfect.

* **Standard Deviations** are substantial for all metrics, indicating variability in performance across queries. Some queries are handled much better than others.

* **LLM and retrieval metrics** are nearly identical, suggesting that the LLM’s answer quality is closely tied to retrieval performance and that the LLM is not adding significant value beyond the retrieved context in this evaluation.

The current system reliably finds most relevant information (high recall), but precision and ranking could be improved. The LLM’s effectiveness is currently limited by retrieval quality, so further gains may come from improving retrieval precision or context selection.
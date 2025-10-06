# 📚 ScienceSage Data & Dataset

This document describes the data sources, dataset construction, and processing pipeline used in ScienceSage.

---

## 🗂️ Data Sources

- **Wikipedia:**  
  The primary data source is Wikipedia, focusing on articles related to space exploration, missions, celestial bodies, technologies, and key events.

--

## 🖼️ Data Columns Overview

<div align="center">
  <img src="../images/sciencesage_data_columns.png" alt="ScienceSage Data Columns" width="500"/>
</div>

*This diagram shows the main columns and structure of the processed dataset used for retrieval and answer generation.*

---

## 🏗️ Dataset Construction

1. **Curation:**  
   Relevant Wikipedia pages are selected using space-related keywords, categories, and manual review to ensure coverage of important topics.

2. **Chunking:**  
   Each article is split into smaller, manageable text chunks (typically by paragraph or section) to optimize retrieval and context assembly for the LLM.

3. **Embedding:**  
   Each chunk is embedded using OpenAI’s embedding model, producing vector representations suitable for similarity search.

4. **Storage:**  
   Embedded chunks and their metadata (title, section, source URL) are stored in a Qdrant vector database for efficient retrieval.

5. **Ground Truth Creation:**  
   For evaluation, a set of question–answer pairs is manually created, with ground truth Wikipedia chunks mapped to each question for retrieval metric calculation.

---

## 🔄 Data Processing Pipeline

1. **Collect Wikipedia articles** on space exploration topics.
2. **Preprocess and clean** the text (remove markup, filter irrelevant content).
3. **Chunk articles** into smaller passages.
4. **Embed each chunk** using OpenAI’s embedding API.
5. **Store embeddings** and metadata in Qdrant.
6. **Create evaluation sets** with ground truth mappings for retrieval and answer quality assessment.

---

## 📊 Dataset Usage

- **Retrieval:**  
  When a user asks a question, the system embeds the query and retrieves the most relevant chunks from Qdrant.
- **Answer Generation:**  
  Retrieved chunks are provided as context to GPT-4, which generates answers at the requested complexity level.
- **Evaluation:**  
  Retrieval and answer quality are measured using metrics such as Recall@K, Precision@K, MRR, and nDCG@K.

---

## 📁 File Locations

- **Raw and processed data:**  
  `data/` directory
- **Ground truth and evaluation sets:**  
  `data/ground_truth/`
- **Data processing scripts:**  
  `scripts/` directory

---

## 📄 References

- [docs/ground_truth_format.md](ground_truth_format.md) — Ground truth dataset format and examples
- [docs/retrieval_evaluation_metrics.md](retrieval_evaluation_metrics.md) — Retrieval evaluation metrics
- [docs/setup.md](setup.md) — Data preparation and setup instructions

---
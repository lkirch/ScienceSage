## 🛠️ API Reference

**POST /rag**

- **Input:**  
  ```json
  {
    "query": "What is the Hubble Space Telescope?",
    "top_k": 5
  }
  ```

- **Output:**  
  ```json
  {
    "answer": "...",
    "context_chunks": [...],
    "sources": ["[1] https://en.wikipedia.org/wiki/Hubble_Space_Telescope", ...]
  }
  ```

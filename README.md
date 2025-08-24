#  🧠 ScienceSage
Smart Science, Made Simple

An end-to-end **Retrieval-Augmented Generation (RAG)** project built for the [LLM Zoomcamp Capstone](https://github.com/DataTalksClub/llm-zoomcamp).  
This system helps users **explore complex scientific topics** (like neuroplasticity, AI concepts, renewable energy, animal behavior, and ecosystem interactions) at **different levels of explanation**:

- 🏫 **Middle School** (simple, intuitive)  
- 🎓 **College** (intermediate, with more depth)  
- 🧪 **Advanced** (detailed, technical)

Powered by **GPT-4**, **Qdrant**, and **Streamlit**, and developed in **Codespaces (Python 3.12)**.

---

## ✨ Features
- **End-to-end RAG pipeline** (OpenAI GPT + Qdrant vector DB).  
- **Multi-level answers** (simple → advanced).  
- **Public domain data sources** (NASA, Wikipedia, Stanford).  
- **Feedback system** (👍 / 👎 per answer, stored for analysis).  
- **Streamlit interface** with example queries and sidebar controls.  

---

## 🔹 Topics
- **Neuroplasticity** (psych/neuro)
- **AI Concepts** (transformers, RAG, embeddings, etc.)
- **Renewable Energy & Climate Change**
- **Animal Adaptation/Behavior**
- **Ecosystem Interactions**

---

## 📂 Project Structure
```
ScienceSage/
│
├── app/ # Application (Streamlit + backend logic)
│ ├── app.py # Streamlit UI
│ ├── retrieval_system.py # Query → retrieve → GPT pipeline
│ ├── feedback_manager.py # Save thumbs up/down
│ ├── analyze_feedback.py # Summarize user feedback
│ └── config.py # API keys & settings
│
├── data/ # Data sources & outputs
│ ├── raw/ # Original files (html, pdf, etc.)
│ ├── processed/ # Clean text files
│ └── chunks/ # JSONL with chunked docs
│
├── notebooks/ # Jupyter exploration
│ └── sanity_check.ipynb
│
├── scripts/ # Utilities
│ ├── download_and_clean.py # Download NASA/Wikipedia/PDF → text
│ ├── preprocess.py # Chunk text → JSONL
│ ├── embed.py # Embed chunks → Qdrant
│ └── test_qdrant.py # Sanity check retrieval
│
├── docker/ # Docker setup
│ └── Dockerfile
│
├── tests/ # Unit/integration tests
│ └── test_pipeline.py
│
├── requirements.txt # Python dependencies
├── README.md # This file
├── .env.example # Example API keys (not committed)
└── .gitignore
```

---

## 📊 Data Sources (Public Domain)

- **Neuroplasticity**: [Wikipedia](https://en.wikipedia.org/wiki/Neuroplasticity)  
- **AI Concepts**:  
  - [Wikipedia – Transformer (ML)](https://en.wikipedia.org/wiki/Transformer_(machine_learning))  
  - [Stanford CS324 LLM Lectures (CC BY-SA)](https://web.stanford.edu/class/cs324/)  
- **Climate Change & Renewable Energy**: [NASA Climate Change](https://climate.nasa.gov/)  
- **Animal Behavior & Ecosystems**:  
  - [Smithsonian Open Access](https://www.si.edu/openaccess)  
  - [Wikipedia – Animal Migration](https://en.wikipedia.org/wiki/Animal_migration)  

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/lkirch/ScienceSage.git
cd ScienceSage
```

### 2. Create a virtual environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the environment variables
Copy `.env.example` → `.env` and fill in:
```ini
OPENAI_API_KEY=sk-xxxx
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Prepare the data
```bash
python scripts/download_and_clean.py   # fetch & clean NASA/Wikipedia/PDF
python scripts/preprocess.py           # chunk into JSONL
python scripts/embed.py                # embed & store in Qdrant
```

### 5. Run the Streamlit app
```bash
streamlit run app/app.py
```

---

🖥️ Usage

- Select a topic in the sidebar (AI, Neuroplasticity, Climate, etc.).
- Ask a question (e.g., "Explain transformers like I’m 12").
- Choose answer complexity (Middle School / College / Advanced).
- Get a generated answer with citations to sources.
- Provide feedback via 👍 / 👎.

---

💡 Example Queries

Here are some example questions to try for each topic:

🧠 Neuroplasticity

- Middle School: "What is neuroplasticity, like I’m 10 years old?"
- College: "How does neuroplasticity help stroke patients recover?"
- Advanced: "Explain synaptic pruning and its role in neuroplasticity."

🤖 AI Concepts

- Middle School: "What is a transformer in AI, explained simply?"
- College: "How do attention mechanisms work in transformers?"
- Advanced: "Compare RAG with fine-tuning for knowledge integration."

🌍 Climate Change & Renewable Energy

- Middle School: "Why is Earth getting hotter?"
- College: "What are the main human causes of climate change?"
- Advanced: "Explain how feedback loops (like melting ice) accelerate climate change."

🐦 Animal Behavior

- Middle School: "Why do birds fly south for the winter?"
- College: "How do animals use migration to adapt to seasonal changes?"
- Advanced: "Discuss the role of circadian rhythms in animal migration."

🌱 Ecosystem Interactions

- Middle School: "What is a food chain?"
- College: "How do predators and prey keep an ecosystem balanced?"
- Advanced: "Explain trophic cascades with an example from Yellowstone."

---


🐳 Docker (optional)

To build and run inside a container:
```bash
docker build -t ScienceSage .
docker run -p 8501:8501 --env-file .env ScienceSage
```
Then open: http://localhost:8501

---

🗺️ Roadmap

- [ ] Add reranking for more accurate retrieval.
- [ ] Include images (NASA, Smithsonian) for multimodal answers.
- [ ] Deploy publicly on HuggingFace Spaces or Streamlit Cloud.

--- 

🪪 License

This project uses public domain or CC-BY-SA data sources.
Code is MIT licensed.

---

🙌 Acknowledgements

- [DataTalksClub LLM Zoomcamp] (https://github.com/DataTalksClub/llm-zoomcamp)
- [Qdrant] (https://qdrant.tech/)
- [Streamlit] (https://streamlit.io/)
- [OpenAI] (https://openai.com/)
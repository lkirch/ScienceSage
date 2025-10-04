![ScienceSage Logo](images/nano-banana-generated-logo.jpeg)

# ScienceSage

**ScienceSage** is an end-to-end Retrieval-Augmented Generation (RAG) system that delivers accurate, level-appropriate answers about space exploration, sourced from Wikipedia. Built for the [LLM Zoomcamp Capstone](https://github.com/DataTalksClub/llm-zoomcamp), it adapts explanations for different backgrounds and provides clear citations.

---

## 🤔💭 Problem: Why ScienceSage?

🚀 Space exploration is inspiring but complex. Reliable, accessible information is scattered and rarely tailored to learners’ needs. ScienceSage bridges this gap by:

- Delivering up-to-date answers with Wikipedia citations
- Adapting explanations for different backgrounds:
  - 🏫 **Middle School** (simple, intuitive)
  - 🎓 **College** (intermediate, with more depth)
  - 🧪 **Advanced** (detailed, technical)
- Enabling user feedback to improve over time

---

## 💡 Approach & Features

**ScienceSage** is an end-to-end **Retrieval-Augmented Generation (RAG)** project built for the [LLM Zoomcamp Capstone](https://github.com/DataTalksClub/llm-zoomcamp), powered by **GPT-4**, **Qdrant**, and **Streamlit**, and developed in Codespaces (Python 3.12).

✨ **Features**:
- **End-to-end RAG pipeline** (OpenAI GPT + Qdrant vector DB).  
- **Multi-level answers** (simple → advanced).  
- **Wikipedia as the primary data source** (focused on space exploration).  
- **Feedback system** (👍 / 👎 per answer, stored for analysis).  
- **Streamlit interface** with example queries and sidebar controls.  

📊 **Data Source** : [Wikipedia](https://www.wikipedia.org/) (focused on space exploration topics)

🔹 **Topics covered:**  
Space exploration, missions, Solar System, Mars, Moon, animals in space

---

## 📊 Results

| Metric             | Value   |
|--------------------|---------|
| Retrieval Recall   | 0.82    |
| Answer Accuracy    | 0.76    |
| User Feedback 👍   | 92%     |

*Detailed metrics and evaluation will be added after full pipeline testing.*

---

## 🔜 Future Work

- Support additional science domains and topics
- Add "Rephrase Question" and "Regenerate Answer" features
- Improve feedback analytics and user interaction
- Enable multimedia, images, and multi-language support
- Add async streaming answers, caching, and conversation history

---

## 📂 Project Structure

For an overview of the project structure, see below:  
```
ScienceSage/
├── sciencesage/         # App & backend logic
├── data/                # Data & outputs
├── images/              # Images & diagrams
├── scripts/             # Utilities
├── tests/               # Tests
├── requirements.txt     # Dependencies
├── Makefile             # Common workflows
├── README.md            # This file
└── ...
```

See [docs/project_structure.md](docs/project_structure.md) for the full directory tree and file descriptions.

---

## ⚡ Quickstart Setup

1. **Clone the repo and enter the directory:**
```bash
git clone https://github.com/lkirch/ScienceSage.git
cd ScienceSage
```

2. **Create and activate a virtual environment:**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Copy and edit environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env to add your OpenAI API key
   ```

4. **Start Qdrant (vector database):**
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

5. **Prepare the data:**
   ```bash
   python scripts/download_and_clean.py
   python scripts/preprocess.py
   python scripts/embed.py
   ```

### 6. Run the Streamlit app
```bash
streamlit run sciencesage/app.py
```

- The app will open in your browser (or use $BROWSER http://localhost:8501).

> For detailed setup and advanced options, see [docs/setup.md](docs/setup.md).

---

## 🛠️ Using the Makefile

This project includes a `Makefile` to simplify common setup and run tasks.
See [docs/using_the_makefile.md](docs/using_the_makefile.md) for more details.

---

## 🧪 Running Tests

How to run unit and integration tests, including requirements and tips.

See [docs/testing.md](docs/testing.md) for details on running and writing tests.

---

## 🖥️ Usage

- Select a topic in the sidebar (Space Exploration)
- Choose answer complexity (Middle School / College / Advanced)
- Use an example question or ask a question of your own
- Get a generated answer with citations to Wikipedia sources
- Click the Show retrieved context to view the context returned
- Provide feedback via 👍 / 👎
- Click the Debug Options expander to show debug info

---

## 💡 Example Queries

Here are some example questions to try for space exploration:


🚀 Space Exploration

- Middle School: "What is the International Space Station?"
- College: "How do Mars rovers navigate on the surface?"
- Advanced: "Describe NASA's three-phase official plan for human exploration and colonization of Mars."

---

## ✅ Requirements

All Python dependencies are listed in `requirements.txt`.  
Install with:
```bash
pip install -r requirements.txt
```

---

## 🛠️ API Reference

Details on the RAG API endpoints, input/output formats, and usage examples. Full API documentation: [docs/api-reference.md](docs/api-reference.md)

---

## 🏅 Ground Truth Dataset Format

Format and example for the ground truth dataset used in evaluation. See [docs/ground_truth_format.md](docs/ground_truth_format.md) for dataset details.

---

## 📝 Notes

- The **Streamlit app** in `sciencesage/app.py` is the UI.  
- Make sure to set up your `.env` file with `OPENAI_API_KEY`.
- To open the Streamlit app in your browser from the dev container, use:
  ```bash
  $BROWSER http://localhost:8501
  ```
- All dependencies are managed in `requirements.txt`.

---

## 🙌 Acknowledgements

- [DataTalksClub LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp)
- [GitHub Codespaces](https://github.com/features/codespaces)
- [Wikipedia API](https://pypi.org/project/Wikipedia-API/)
- [Qdrant](https://qdrant.tech/)
- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [Claude](http://claude.ai) and [ChatGPT](http://chatgpt.com) for brainstorming, code debugging and improvements
- [Google's Nano Banana](https://aistudio.google.com/prompts/new_chat?model=gemini-2.5-flash-image-preview) for designing the logo

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue or PR if you have suggestions or improvements.

---
import streamlit as st
from pathlib import Path
from sciencesage.retrieval_system import retrieve_answer, rephrase_query
from sciencesage.feedback_manager import save_feedback
from sciencesage.config import LEVELS, TOPICS
from loguru import logger
from dotenv import load_dotenv
import re
import urllib.parse

load_dotenv()

st.set_page_config(page_title="ScienceSage", layout="wide")

# --- Wider Sidebar with logo & background ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 350px;
        max-width: 350px;
        background-color: #D4E7C5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

logo_path = Path(__file__).parent.parent / "images" / "nano-banana-generated-logo.jpeg"
col_logo, col_title = st.columns([1, 8])
with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=80)
    else:
        st.markdown("<div style='font-size:50px;'>🔬</div>", unsafe_allow_html=True)

with col_title:
    st.markdown(
        """
        <h1 style="color:#9DC183; font-size:2.3em; margin-top:10px;">
            ScienceSage: <span style="color:gray; font-weight:normal;">Smart Science, Made Simple.</span>
        </h1>
        """,
        unsafe_allow_html=True,
    )

st.markdown("Ask me anything about science! Powered by LLMs and Vector Databases.")

# --- Sidebar controls ---
st.sidebar.header("Controls")
topic = st.sidebar.selectbox("Choose a topic", TOPICS)
level = st.sidebar.radio("Select explanation level", LEVELS)

example_queries = {
    "Neuroplasticity": ["What is neuroplasticity?", "How do neurons rewire?"],
    "AI": ["What is a neural network?", "Explain transformers."],
    "Renewable Energy & Climate Change": ["What is the greenhouse effect?", "How do solar panels work?"],
    "Animal Adaptation": ["How do penguins stay warm?", "What is mimicry in animals?"],
    "Ecosystem Interactions": ["What is a food chain?", "How does deforestation affect biodiversity?"]
}

# Initialize session_state for query and rephrased query
if "query" not in st.session_state:
    st.session_state.query = ""
if "rephrased_query" not in st.session_state:
    st.session_state.rephrased_query = ""

# Example query button
if st.sidebar.button("Try Example"):
    st.session_state.query = example_queries[topic][0]
    st.session_state.rephrased_query = ""

# Prompt arrow
st.markdown("""
<span style="color:#9DC183; font-size:1.5em;">&#11013;</span>
<span style="font-size:1.1em;"> Please select a topic and an explanation level on the left, then enter your question below: </span>
<span style="color:#9DC183; font-size:1.5em;">&#11015;</span>
""", unsafe_allow_html=True)

# --- Query input field ---
query_input = st.text_input("Enter your question here", value=st.session_state.query, key="query_input")

# Helper function to format references
def format_reference(url: str):
    if url.startswith("10."):
        url = f"https://doi.org/{url}"
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return domain or url

# --- Main retrieval function ---
def run_retrieval(query: str, topic: str, level: str):
    if not query.strip():
        st.warning("Please enter a question.")
        return

    st.session_state.query = query
    st.session_state.rephrased_query = ""

    # Retrieve answer
    try:
        answer, contexts, references = retrieve_answer(query, topic, level)
        st.session_state.answer = answer
        st.session_state.context = contexts
        st.session_state.references = references
        st.session_state.last_query = query
        st.session_state.last_topic = topic
        st.session_state.last_level = level
    except Exception as e:
        logger.error(f"Error retrieving answer: {e}")
        st.error("An error occurred while retrieving the answer.")
        return

    # -------------------------
    # Low confidence warning
    # -------------------------
    if contexts:
        top_conf = int(contexts[0]["score"] * 100)
        if top_conf < 60:
            st.warning("⚠️ Low confidence – consider rephrasing your question for better results.")

    # -------------------------
    # Replace citations in answer with clickable links
    # -------------------------
    def replace_citation(match):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(st.session_state.references):
            ref = st.session_state.references[idx]
            url = ref["url"]
            domain = format_reference(url)
            return f'<a href="{url}" target="_blank">[{idx+1} - {domain}]</a>'
        return match.group(0)

    answer_with_links = re.sub(r"\[(\d+)\]", replace_citation, answer)

    # -------------------------
    # Display answer
    # -------------------------
    st.subheader("Answer")
    st.markdown(answer_with_links, unsafe_allow_html=True)

    # -------------------------
    # Horizontal scrollable context
    # -------------------------
    st.markdown("### Retrieved Context")
    if contexts:
        st.markdown('<div style="overflow-x:auto; display:flex; gap:10px;">', unsafe_allow_html=True)
        for c in sorted(contexts, key=lambda x: x['score'], reverse=True):
            conf = int(c["score"] * 100)
            color = "green" if conf > 85 else "orange" if conf > 60 else "red"
            st.markdown(f'''
                <div style="min-width:300px; padding:8px; margin-bottom:5px; border-left:3px solid #9DC183;
                            background-color:#f9f9f9; border-radius:5px;">
                    <b>{c['source']} (chunk {c['chunk']})</b><br>
                    <span style="color:{color}; font-weight:bold;">[Confidence: {conf}%]</span><br>
                    {c['text']}
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No context retrieved.")

    # -------------------------
    # Horizontal scrollable references
    # -------------------------
    st.markdown("### 🔗 References")
    if references:
        # Merge URLs by snippet
        merged_refs = {}
        for r in references:
            key = r["snippet"]
            if key not in merged_refs:
                merged_refs[key] = {"urls": [r["url"]], "score": r["score"], "snippet": r["snippet"]}
            else:
                merged_refs[key]["urls"] = list(set(merged_refs[key]["urls"] + [r["url"]]))
        st.markdown('<div style="overflow-x:auto; display:flex; gap:10px;">', unsafe_allow_html=True)
        for idx, ref in enumerate(merged_refs.values(), start=1):
            conf = int(ref["score"] * 100)
            color = "green" if conf > 85 else "orange" if conf > 60 else "red"
            urls_links = ", ".join([f'<a href="{u}" target="_blank">{format_reference(u)}</a>' for u in ref["urls"]])
            st.markdown(f'''
                <div style="min-width:250px; padding:8px; margin-bottom:5px; border:1px solid #ccc;
                            border-radius:10px; background-color:#f9f9f9;">
                    <b>[{idx}]</b> {urls_links}
                    <span style="color:{color}; font-weight:bold;">({conf}% match)</span><br>
                    <small style="color: gray;">{ref["snippet"]}</small>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No references retrieved.")

# -------------------------
# Buttons: Rephrase & Regenerate (inline)
# -------------------------
st.markdown("### Actions")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("Get Answer"):
        run_retrieval(query_input, topic, level)
with col2:
    if st.button("Rephrase Question"):
        if query_input.strip():
            rephrased = rephrase_query(query_input, topic)
            st.session_state.rephrased_query = rephrased
            run_retrieval(rephrased, topic, level)
with col3:
    if st.button("Regenerate Answer"):
        q_to_use = st.session_state.rephrased_query or query_input
        run_retrieval(q_to_use, topic, level)

# -------------------------
# Feedback buttons (inline)
# -------------------------
st.markdown("### Feedback on this answer")
fb_col1, fb_col2 = st.columns([1, 1])
with fb_col1:
    if st.button("👍", key="feedback_up"):
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "up"
        )
        st.success("Thanks for your feedback! 👍")
        logger.info("User gave positive feedback")
with fb_col2:
    if st.button("👎", key="feedback_down"):
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "down"
        )
        st.success("Thanks for your feedback! 👎")
        logger.info("User gave negative feedback")
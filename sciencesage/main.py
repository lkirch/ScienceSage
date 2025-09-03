import streamlit as st
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.feedback_manager import save_feedback
from sciencesage.config import LEVELS, TOPICS
import re
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

st.image("../images/nano-banana-generated-logo.jpeg", width=120)

st.set_page_config(page_title="ScienceSage", layout="wide")

# Sage green hex: #9DC183
st.markdown(
    '<h1 style="color:#9DC183; font-size:2.5em; margin-bottom:0.2em;">🔬 ScienceSage</h1>',
    unsafe_allow_html=True
)
st.markdown('<span style="font-size:1.2em;color:gray;">"Smart Science, Made Simple."</span>', unsafe_allow_html=True)

# Sidebar
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

if st.sidebar.button("Try Example"):
    st.session_state.query = example_queries[topic][0]

query = st.text_input("Enter your question:", key="query")

def run_retrieval(query: str, topic: str, level: str):
    """Shared helper for retrieving and displaying answers."""
    try:
        answer, context, references = retrieve_answer(query, topic, level)
        st.session_state.answer = answer
        st.session_state.context = context
        st.session_state.references = references
        st.session_state.last_query = query
        st.session_state.last_topic = topic
        st.session_state.last_level = level
    except Exception as e:
        logger.error(f"Error retrieving answer: {e}")
        st.error("An error occurred while retrieving the answer.")
        return
    
    if references:
        def replace_citation(match):
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(references):
                url = references[idx]
                return f"[{idx+1}]({url})"
            return match.group(0)

        answer_with_links = re.sub(r"\[(\d+)\]", replace_citation, answer)
    else:
        answer_with_links = answer

    st.subheader("Answer")
    st.markdown(answer_with_links, unsafe_allow_html=True)

    with st.expander("Show retrieved context"):
        if st.session_state.context:
            if isinstance(st.session_state.context, (list, tuple)):
                st.markdown("\n\n".join(str(c) for c in st.session_state.context))
            else:
                st.markdown(str(st.session_state.context))
        else:
            st.info("No context retrieved.")

    if references:
        st.markdown("### 🔗 References")
        for idx, url in enumerate(references, start=1):
            st.markdown(f"- [{idx}]({url})")

# --- Buttons ---
if st.button("Get Answer"):
    if query.strip():
        logger.info(f"User submitted query: '{query[:50]}...', topic: '{topic}', level: '{level}'")
        with st.spinner("Retrieving answer..."):
            run_retrieval(query, topic, level)
    else:
        st.warning("Please enter a question.")

# Feedback
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👍", key="up"):
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "up"
        )
        logger.info("User gave positive feedback")
with col2:
    if st.button("👎", key="down"):
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "down"
        )
        logger.info("User gave negative feedback")
with col3:
    if st.button("🔄 Regenerate", key="regen"):
        if "last_query" in st.session_state:
            run_retrieval(st.session_state.last_query, st.session_state.last_topic, st.session_state.last_level)
            logger.info("User requested answer regeneration")
        else:
            st.warning("No previous query to regenerate.")
            logger.info("User requested answer regeneration without a previous query")

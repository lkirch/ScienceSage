import streamlit as st
from pathlib import Path
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.feedback_manager import save_feedback
from sciencesage.config import LEVELS, TOPICS
from loguru import logger
from dotenv import load_dotenv
import re
import urllib.parse

load_dotenv()

st.set_page_config(page_title="ScienceSage", layout="wide")

# --- Wider Sidebar ---
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

# --- Sidebar ---
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

if "query" not in st.session_state:
    st.session_state.query = ""

if st.sidebar.button("Try Example"):
    st.session_state.query = example_queries[topic][0]

arrow_prompt = """
<span style="color:#9DC183; font-size:1.5em;">&#11013;</span>
<span style="font-size:1.1em;"> Please select a topic and an explanation level on the left, then enter your question below: </span>
<span style="color:#9DC183; font-size:1.5em;">&#11015;</span>
"""
st.markdown(arrow_prompt, unsafe_allow_html=True)

query = st.text_input("", key="query", label_visibility="collapsed")


# -------------------------
# Helper Functions
# -------------------------
def format_reference(url: str):
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return domain or url


def run_retrieval(query: str, topic: str, level: str):
    """Retrieve answer and display with enhanced references, context, and diagnostics."""
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

    # -------------------------
    # Replace citations in answer with tooltips
    # -------------------------
    if references:
        def replace_citation(match):
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(references):
                url = references[idx] if isinstance(references[idx], str) else references[idx].get("url", "")
                domain = format_reference(url)
                return f'<span title="{url}">[{idx+1} - {domain}]</span>'
            return match.group(0)

        answer_with_links = re.sub(r"\[(\d+)\]", replace_citation, answer)
    else:
        answer_with_links = answer

    # -------------------------
    # Display Answer
    # -------------------------
    st.subheader("Answer")
    st.markdown(answer_with_links, unsafe_allow_html=True)

    # -------------------------
    # Enhanced Context Display
    # -------------------------
    with st.expander("Show retrieved context"):
        if st.session_state.context:
            for idx, chunk in enumerate(st.session_state.context, start=1):
                # Expect chunk format: [source:chunk_index] text
                match = re.match(r"\[(.*?):(.*?)\]\s*(.*)", chunk)
                if match:
                    source, chunk_index, text = match.groups()
                    st.markdown(
                        f"""
                        <div style="padding:8px; margin-bottom:8px; border-left:3px solid #9DC183;
                                    background-color:#f9f9f9; border-radius:5px;">
                            <b>{source} (chunk {chunk_index})</b><br>
                            {text}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(chunk)
        else:
            st.info("No context retrieved.")

    # -------------------------
    # Display References as Cards
    # -------------------------
    if references:
        st.markdown("### 🔗 References")
        for idx, ref in enumerate(references, start=1):
            url = ref if isinstance(ref, str) else ref.get("url", "")
            snippet = ""
            if isinstance(ref, dict):
                snippet = ref.get("text", "")[:200] + "..."
            domain = format_reference(url)
            st.markdown(
                f"""
                <div style="padding: 10px; margin-bottom: 10px; border: 1px solid #ccc;
                            border-radius: 10px; background-color: #f9f9f9;">
                    <b>[{idx}]</b> <a href="{url}" target="_blank">{domain}</a><br>
                    <small style="color: gray;">{snippet}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------
    # Retrieval Diagnostics
    # -------------------------
    with st.expander("Retrieval Diagnostics (for debugging)"):
        if st.session_state.context:
            st.markdown("**Number of chunks retrieved:** " + str(len(st.session_state.context)))
        if references:
            st.markdown("**References detected:**")
            for idx, ref in enumerate(references, start=1):
                st.markdown(f"- {idx}: {format_reference(ref if isinstance(ref, str) else ref.get('url',''))}")


# -------------------------
# Buttons
# -------------------------
if st.button("Get Answer"):
    if query.strip():
        logger.info(f"User submitted query: '{query[:50]}...', topic: '{topic}', level: '{level}'")
        with st.spinner("Retrieving answer..."):
            run_retrieval(query, topic, level)
    else:
        st.warning("Please enter a question.")

# -------------------------
# Feedback Buttons
# -------------------------
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
        st.success("Thanks for your feedback! 👍")
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
        st.success("Thanks for your feedback! 👎")
        logger.info("User gave negative feedback")
with col3:
    if st.button("🔄 Regenerate", key="regen"):
        if "last_query" in st.session_state:
            run_retrieval(st.session_state.last_query, st.session_state.last_topic, st.session_state.last_level)
            logger.info("User requested answer regeneration")
        else:
            st.warning("No previous query to regenerate.")
            logger.info("User requested answer regeneration without a previous query")

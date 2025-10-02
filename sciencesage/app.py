import streamlit as st
from pathlib import Path
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.feedback_manager import save_feedback
from sciencesage.config import LEVELS, TOPICS, EXAMPLE_QUERIES
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

st.markdown("""
<div style="margin-bottom: 1em; font-size: 1.1em;">
    🚀 <b>Curious about science?</b> Ask any question, big or small!<br>
    <span style="color:#9DC183;">
        <b>Tip:</b> For the best experience, try asking about Space Exploration — missions, discoveries, challenges, or the mysteries of our universe.
    </span>
</div>
""", unsafe_allow_html=True)

example_queries = EXAMPLE_QUERIES

# Initialize session_state for query and answer
if "query" not in st.session_state:
    st.session_state.query = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""

# Prompt arrow
st.markdown("""
<span style="color:#9DC183; font-size:1.5em;">&#11013;</span>
<span style="font-size:1.1em;"> Please select a topic and an explanation level on the left.  You can use one of our examples or type in your own question: </span>
<span style="color:#9DC183; font-size:1.5em;">&#11015;</span>
""", unsafe_allow_html=True)


def format_answer_with_sources(answer: str, sources: dict) -> str:
    # Replace [Source chunk N](url) or Source chunk N with markdown links if possible
    def repl_chunk(match):
        chunk_id = f"chunk {match.group(1)}"
        url = sources.get(chunk_id)
        if url and url != "#":
            return f"[Source {chunk_id}]({url})"
        else:
            return f"Source {chunk_id}"

    # Replace Source chunk N (with or without punctuation) with markdown link if possible
    answer = re.sub(r"Source chunk (\d+)\.?", repl_chunk, answer)

    # Collect all URLs and chunk IDs actually referenced in the answer
    referenced_chunks = set(re.findall(r"Source (chunk \d+)", answer))
    referenced_urls = set(re.findall(r"\[Source (chunk \d+)\]\((https?://[^\)]+)\)", answer))
    # Also find any bare URLs in the "External reference URLs" section
    external_urls = set(re.findall(r"https?://[^\s\)\]]+", answer))

    # Build references: show URLs and chunk numbers actually cited
    refs = []
    # Add referenced URLs with chunk numbers
    for chunk_id, url in referenced_urls:
        refs.append(f"{url} ({chunk_id})")
    # Add any Source chunk N that didn't have a URL
    for chunk_id in referenced_chunks:
        if not any(chunk_id == c for c, _ in referenced_urls):
            url = sources.get(chunk_id)
            if url and url != "#":
                refs.append(f"{url} ({chunk_id})")
            else:
                refs.append(f"Source {chunk_id}")
    # Add any external URLs not already listed
    for url in external_urls:
        if not any(url in ref for ref in refs):
            refs.append(url)

    # Only append references if not already present in the answer
    if refs and "references:" not in answer.lower():
        refs_md = "\n".join(f"- {ref}" for ref in refs)
        answer += "\n\n**References:**\n" + refs_md
    return answer

# --- Main retrieval function ---
def run_retrieval(query: str, topic: str, level: str):
    if not query.strip():
        st.warning("Please enter a question.")
        return

    try:
        result = retrieve_answer(query, topic, level)
        answer = result.get("answer", "")
        sources = result.get("sources", {})
        formatted_answer = format_answer_with_sources(answer, sources)
        st.session_state.answer = formatted_answer
        st.session_state.last_query = query
        st.session_state.last_topic = topic
        st.session_state.last_level = level
    except Exception as e:
        logger.error(f"Error retrieving answer: {e}")
        st.error("An error occurred while retrieving the answer.")
        return

    # Display answer
    st.markdown("""
    <style>
    .full-width-container > div {
        flex: 1 1 0%;
        min-width: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container():
        st.subheader("Answer")
        st.markdown(st.session_state.answer, unsafe_allow_html=True)

def update_example_query():
    level_idx = LEVELS.index(st.session_state.level) if st.session_state.level in LEVELS else 0
    example = EXAMPLE_QUERIES[st.session_state.topic][level_idx]
    all_examples = [q for topic_examples in EXAMPLE_QUERIES.values() for q in topic_examples]
    if (
        st.session_state.query == "" or
        st.session_state.query in all_examples
    ):
        st.session_state.query = example
        st.session_state.answer = ""

# Build mapping: display name -> original topic
TOPIC_DISPLAY_MAP = {t.replace("Category:", "").strip(): t for t in TOPICS}
TOPIC_DISPLAY_NAMES = list(TOPIC_DISPLAY_MAP.keys())

# --- Sidebar controls ---
st.sidebar.header("Controls")
selected_display_topic = st.sidebar.selectbox(
    "Choose a topic:",
    TOPIC_DISPLAY_NAMES,
    key="display_topic",
    on_change=update_example_query
)
# Map back to original topic key for internal use
st.session_state.topic = TOPIC_DISPLAY_MAP[selected_display_topic]

st.sidebar.radio(
    "Select explanation level:",
    LEVELS,
    key="level",
    on_change=update_example_query
)

if st.sidebar.button("Try Example"):
    level_idx = LEVELS.index(st.session_state.level) if st.session_state.level in LEVELS else 0
    st.session_state.query = EXAMPLE_QUERIES[st.session_state.topic][level_idx]
    st.session_state.answer = ""

# --- Get current topic and level from session state ---
topic = st.session_state.topic
level = st.session_state.level

# --- Query input field ---
query = st.text_input(
    "Enter your question here:",
    key="query",
    on_change=lambda: run_retrieval(st.session_state.query, topic, level)
)

# -------------------------
# Get Answer button (single, full width)
# -------------------------
if st.button("Get Answer"):
    run_retrieval(st.session_state.query, topic, level)

# -------------------------
# Feedback buttons
# -------------------------
st.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-top: 1em;">
    <span style="font-weight: 600; font-size: 1.1em;">Feedback on this answer:</span>
</div>
""", unsafe_allow_html=True)

fb_col1, fb_col2 = st.columns([0.07, 0.07])
feedback_msg = ""
with fb_col1:
    if st.button("👍", key="feedback_up"):
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "up"
        )
        feedback_msg = "Thanks for your feedback! 👍"
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
        feedback_msg = "Thanks for your feedback! 👎"
        logger.info("User gave negative feedback")

if feedback_msg:
    st.success(feedback_msg)


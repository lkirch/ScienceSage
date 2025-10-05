import streamlit as st
from pathlib import Path
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.feedback_manager import save_feedback
from sciencesage.config import LEVELS, TOPICS, EXAMPLE_QUERIES
from loguru import logger
from dotenv import load_dotenv
import re

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
<span style="font-size:1.1em;"> Please select both a topic and an explanation level on the left.  You can use one of our examples or type in your own question: </span>
<span style="color:#9DC183; font-size:1.5em;">&#11015;</span>
""", unsafe_allow_html=True)


def format_answer_with_sources(answer: str, sources: dict) -> str:
    # Remove "External reference URLs" section
    external_urls = set()
    def extract_urls(match):
        urls = re.findall(r"https?://[^\s\)\]]+", match.group(0))
        external_urls.update(urls)
        return ""
    answer = re.sub(r"External reference URLs:\s*((?:https?://[^\s\)\]]+\s*)+)", extract_urls, answer, flags=re.IGNORECASE)

    # Remove any existing "References:" section (and everything after it)
    answer = re.sub(r"\n*References:\n(.|\n)*", "", answer, flags=re.IGNORECASE)

    # Find all URLs in sources, mapping chunk to url
    chunk_url_map = {chunk: url for chunk, url in sources.items() if url and url != "#"}
    source_urls = set(chunk_url_map.values())

    # Find any bare URLs in the answer
    bare_urls = set(re.findall(r"https?://[^\s\)\]]+", answer))

    # Combine all URLs and map them to their chunk references if available
    url_to_chunks = {}
    for chunk, url in chunk_url_map.items():
        url_to_chunks.setdefault(url, set()).add(chunk)
    for url in external_urls | bare_urls:
        url_to_chunks.setdefault(url, set())

    # Build references markdown, sorted for consistency
    refs_md = ""
    if url_to_chunks:
        refs = []
        for url in sorted(url_to_chunks):
            chunks = url_to_chunks[url]
            if chunks:
                refs.append(f"- {url} {'(' + ', '.join(sorted(chunks)) + ')'}")
            else:
                refs.append(f"- {url}")
        refs_md = "\n".join(refs)
        answer = answer.strip() + "\n\n**References:**\n" + refs_md

    return answer

# --- Debugging controls ---
with st.sidebar.expander("🛠️ Debug Options", expanded=False):
    show_debug = st.checkbox("Show debug info", value=False, key="show_debug")
    if show_debug:
        st.write("Session State:", dict(st.session_state))

# --- Main retrieval function ---
def run_retrieval(query: str, topic: str, level: str):
    if not query.strip():
        st.warning("Please enter a question.")
        return

    try:
        result = retrieve_answer(query, topic, level)
        answer = result.get("answer", "")
        sources = result.get("sources", {})
        context_chunks = result.get("context", [])
        formatted_answer = format_answer_with_sources(answer, sources)
        st.session_state.answer = formatted_answer
        st.session_state.last_query = query
        st.session_state.last_topic = topic
        st.session_state.last_level = level
        st.session_state.last_context = context_chunks
        st.session_state.last_raw_result = result  # For debug display

    except Exception as e:
        logger.error(f"Error retrieving answer: {e}")
        st.error("An error occurred while retrieving the answer.")
        if st.session_state.get("show_debug"):
            st.exception(e)
        return

    st.subheader("Answer")
    st.markdown(st.session_state.answer, unsafe_allow_html=True)

    # --- Expandable context display (always visible) ---
    with st.expander("Show retrieved context"):
        if context_chunks:
            for idx, chunk in enumerate(context_chunks, 1):
                st.markdown(f"**Chunk {idx}:**")
                st.markdown(f"> {chunk.get('text', '')}")
                url = chunk.get('source_url')
                if url:
                    st.markdown(f"[Source Link]({url})")
                st.markdown("---")
        else:
            st.markdown("_No context retrieved for this answer._")

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

# --- About/Help expander under Try Example ---
with st.sidebar.expander("ℹ️ About / Help", expanded=False):
    st.markdown("""
    **How to Use ScienceSage**

    1. Choose a topic and explanation level on the left.
    2. Enter your space science question in the box on the right or select an example question.
    4. Submit to get an answer with sources.

    **Explanation Levels**
    - **Middle School**: Simple, easy-to-understand answers.
    - **College**: More detail, for curious learners.
    - **Advanced**: In-depth, technical explanations.

    **Tips**
    - Use the thumbs up 👍 / thumbs down 👎 to rate answers.
    - Expand “Show retrieved context” to see where information came from.

    [Full documentation](https://github.com/lkirch/ScienceSage/blob/main/docs/about_sciencesage.md)
    """)

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


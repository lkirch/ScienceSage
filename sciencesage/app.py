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
        <b>Tip:</b> For the best experience, try asking about <u>space exploration</u>—missions, discoveries, challenges, or the mysteries of our universe.
    </span>
</div>
""", unsafe_allow_html=True)

# --- Sidebar controls ---
st.sidebar.header("Controls")
topic = st.sidebar.selectbox("Choose a topic:", TOPICS)
level = st.sidebar.radio("Select explanation level:", LEVELS)

example_queries = EXAMPLE_QUERIES

# Initialize session_state for query and answer
if "query" not in st.session_state:
    st.session_state.query = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""

# Example query button
if st.sidebar.button("Try Example"):
    # Map level to index
    level_idx = LEVELS.index(level) if level in LEVELS else 0
    st.session_state.query = example_queries[topic][level_idx]
    st.session_state.answer = ""

# Prompt arrow
st.markdown("""
<span style="color:#9DC183; font-size:1.5em;">&#11013;</span>
<span style="font-size:1.1em;"> Please select a topic and an explanation level on the left, then enter your question below or click on the <b>Try Example</b> button to use one of our questions: </span>
<span style="color:#9DC183; font-size:1.5em;">&#11015;</span>
""", unsafe_allow_html=True)

# --- Main retrieval function ---
def run_retrieval(query: str, topic: str, level: str):
    if not query.strip():
        st.warning("Please enter a question.")
        return

    st.session_state.query = query

    # Retrieve answer
    try:
        answer = retrieve_answer(query, topic, level)
        st.session_state.answer = answer
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

# --- Query input field ---
query_input = st.text_input(
    "Enter your question here:",
    value=st.session_state.query,
    key="query_input",
    on_change=lambda: run_retrieval(st.session_state.query_input, topic, level)
)

# -------------------------
# Get Answer button (single, full width)
# -------------------------
if st.button("Get Answer"):
    run_retrieval(query_input, topic, level)

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
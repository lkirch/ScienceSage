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
topic = st.sidebar.selectbox("Choose a topic", TOPICS)
level = st.sidebar.radio("Select explanation level", LEVELS)

example_queries = {
    "Space exploration": [
        "Who was the first human to travel into outer space, and in which spacecraft did they fly?",
        "What are the main rationales for space exploration?",
        "WHow has international cooperation in space exploration evolved since the Space Race era, and what are the current examples of major cooperative programs?"
    ],
    "Category:Space missions": [
        "What was the objective of the Voyager missions?",
        "How do robotic space missions differ from crewed missions?",
        "Which space missions have explored the outer planets?"
    ],
    "Category:Discovery and exploration of the Solar System": [
        "What astronomical object was the first artificial satellite launched into space?",
        "What was the significance of Johannes Kepler's work with Mars and how did it advance our understanding of the Solar System?",
        "HHow have technological developments in astronomy and physics contributed to the redefinition of the Solar System from a geocentric to a heliocentric model?"
    ],
    "Category:Exploration of Mars": [
        "What are the names of the two NASA rovers currently operating on the surface of Mars?",
        "What is the main reason for the high failure rate of missions sent to Mars?",
        "What is NASA's three-phase official plan for human exploration and colonization of Mars?"
    ],
    "Category:Exploration of the Moon": [
        "Who were the first astronauts to land on the Moon, and in which year did this happen?",
        "What significant firsts were achieved by China's Chang'e program on the Moon?",
        "What are NASA's Artemis program goals and the scientific and logistical objectives supporting the return to the Moon?"
    ],
    "Animals in space": [
        "Why were animals sent into space before humans?",
        "What have we learned from animal experiments in space?",
        "Which animals have traveled the farthest from Earth?"
    ]
}

# Initialize session_state for query and answer
if "query" not in st.session_state:
    st.session_state.query = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""

# Example query button
if st.sidebar.button("Try Example"):
    st.session_state.query = example_queries[topic][0]
    st.session_state.answer = ""

# Prompt arrow
st.markdown("""
<span style="color:#9DC183; font-size:1.5em;">&#11013;</span>
<span style="font-size:1.1em;"> Please select a topic and an explanation level on the left, then enter your question below: </span>
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
    "Enter your question here",
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
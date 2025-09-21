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
    "Space exploration": [
        "What are the main challenges of sending humans to Mars?",
        "How has space exploration advanced our understanding of the universe?",
        "What technologies are essential for deep space missions?"
    ],
    "Category:Space missions": [
        "What was the objective of the Voyager missions?",
        "How do robotic space missions differ from crewed missions?",
        "Which space missions have explored the outer planets?"
    ],
    "Category:Discovery and exploration of the Solar System": [
        "How were the planets in our solar system discovered?",
        "What are the most important discoveries about the solar system in the last 50 years?",
        "How do scientists study asteroids and comets?"
    ],
    "Category:Exploration of Mars": [
        "What have we learned from the Mars rover missions?",
        "Why is Mars considered a candidate for future human colonization?",
        "What challenges do robots face when exploring Mars?"
    ],
    "Category:Exploration of the Moon": [
        "What did the Apollo missions discover about the Moon?",
        "How do modern lunar missions differ from those in the 20th century?",
        "What is the significance of water ice on the Moon?"
    ],
    "Animals in space": [
        "Why were animals sent into space before humans?",
        "What have we learned from animal experiments in space?",
        "Which animals have traveled the farthest from Earth?"
    ]
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

# --- Helper function to format references
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
        if 0 <= idx < len(st.session_state.context):
            c = st.session_state.context[idx]
            url = c.get("url", "#")
            domain = format_reference(url)
            chunk_info = f'{c.get("source", "unknown source")} (chunk {c.get("chunk", "?")})'
            return f'<a href="{url}" target="_blank">[{idx+1} - {domain}]</a> <span style="color:gray;font-size:0.9em;">{chunk_info}</span>'
        return match.group(0)

    answer_with_links = re.sub(r"\[(\d+)\]", replace_citation, answer)

    # -------------------------
    # Display answer and context using full width
    # -------------------------
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
        st.markdown(answer_with_links, unsafe_allow_html=True)

        # --- Retrieved Context in expandable section ---
        with st.expander("Show Retrieved Context"):
            if contexts:
                st.markdown('<div style="overflow-x:auto; display:flex; gap:10px;">', unsafe_allow_html=True)
                for c in sorted(contexts, key=lambda x: x['score'], reverse=True):
                    conf = int(c["score"] * 100)
                    color = "green" if conf > 85 else "orange" if conf > 60 else "red"
                    url_display = (
                        f'<b><a href="{c.get("url", "#")}" target="_blank">{format_reference(c.get("url", "#"))}</a></b>'
                        if c.get("url") else "<b>No URL</b>"
                    )
                    chunk_info = f'{c.get("source", "unknown source")} (chunk {c.get("chunk", "?")})'
                    st.markdown(f'''
                        <div style="min-width:300px; padding:8px; margin-bottom:5px; border-left:3px solid #9DC183;
                                    background-color:#f9f9f9; border-radius:5px;">
                            {url_display}<br>
                            <span style="color:gray; font-size:0.95em;">{chunk_info}</span><br>
                            <span style="color:{color}; font-weight:bold;">[Confidence: {conf}%]</span><br>
                            {c['text']}
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No context retrieved.")

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

# -------------------------
# Rephrase and Regenerate section
# -------------------------
st.markdown("""
<div style="margin-top: 1.5em; margin-bottom: 0.5em;">
    <span style="font-weight: 600; font-size: 1.1em;">Rephrase and Regenerate</span>
</div>
""", unsafe_allow_html=True)

rr_col1, rr_col2 = st.columns([0.15, 0.15])
with rr_col1:
    if st.button("Rephrase Question"):
        if st.session_state.query_input.strip():
            rephrased = rephrase_query(st.session_state.query_input)
            st.session_state.rephrased_query = rephrased
            run_retrieval(rephrased, topic, level)
with rr_col2:
    if st.button("Regenerate Answer"):
        run_retrieval(st.session_state.query_input, topic, level)
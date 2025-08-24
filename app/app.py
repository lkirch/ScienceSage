import streamlit as st
from retrieval_system import retrieve_answer
from feedback_manager import save_feedback
from config import LEVELS, TOPICS

st.set_page_config(page_title="ScienceSage", layout="wide")

st.title("🔬 ScienceSage")
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

if st.button("Get Answer"):
    if query.strip():
        with st.spinner("Retrieving answer..."):
            answer, context = retrieve_answer(query, topic, level)
        st.subheader("Answer")
        st.write(answer)

        with st.expander("Show retrieved context"):
            if context:
                if isinstance(context, (list, tuple)):
                    st.markdown("\n\n".join(str(c) for c in context))
                else:
                    st.markdown(str(context))
            else:
                st.info("No context retrieved.")

        # Feedback
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍", key="up"):
                save_feedback(query, answer, topic, level, "up")
        with col2:
            if st.button("👎", key="down"):
                save_feedback(query, answer, topic, level, "down")
        with col3:
            if st.button("🔄 Regenerate", key="regen"):
                answer, context = retrieve_answer(query, topic, level)
                st.write(answer)
    else:
        st.warning("Please enter a question.")

import streamlit as st

def test_query_preserved_on_regenerate(monkeypatch):
    # Simulate session state
    st.session_state["last_query"] = "What is AI?"
    st.session_state["last_topic"] = "AI"
    st.session_state["last_level"] = "College"
    st.session_state["answer"] = "AI is..."
    # Patch retrieval
    monkeypatch.setattr(
        "sciencesage.retrieval_system.retrieve_answer",
        lambda q, t, l: ("AI is...", ["context"], ["http://ref"])
    )
    # Simulate regenerate button logic
    from sciencesage.main import run_retrieval
    run_retrieval(st.session_state.last_query, st.session_state.last_topic, st.session_state.last_level)
    assert st.session_state["answer"] == "AI is..."

def test_query_cleared_on_new_example(monkeypatch):
    st.session_state["query"] = "Old question"
    # Simulate example selection
    from sciencesage.main import example_queries
    topic = "AI"
    st.session_state["query"] = example_queries[topic][0]
    assert st.session_state["query"] == "What is a neural network?"
import pytest
import os
from streamlit.testing.v1 import AppTest

@pytest.fixture(scope="module")
def app():
    """Load the Streamlit app once for all UI tests."""
    # Ensure we run from project root so relative paths (like images) resolve
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    return AppTest.from_file("sciencesage/main.py")

def test_app_renders_without_crashing(app):
    app.run()
    assert not app.exception
    assert any("ScienceSage" in el.value for el in app.markdown)

def test_sidebar_controls_render(app):
    app.run()
    topic_selector = [w for w in app.sidebar.selectbox if "Choose a topic" in w.label]
    level_radio = [w for w in app.sidebar.radio if "Select explanation level" in w.label]
    assert topic_selector, "Topic selectbox not found in sidebar"
    assert level_radio, "Level radio buttons not found in sidebar"

def test_query_input_and_button(app, monkeypatch):
    monkeypatch.setattr(
        "sciencesage.main.retrieve_answer",
        lambda q, t, l: ("Mocked answer", ["context1", "context2"], ["http://example.com"])
    )
    app.run()
    query_box = app.text_input[0]
    query_box.set_value("What is AI?")
    button = [b for b in app.button if b.label == "Get Answer"]
    assert button, "Get Answer button not found"
    button[0].click().run()
    # Debug: print all markdowns and expander markdowns
    print("Top-level markdowns:", [el.value for el in app.markdown])
    for exp in app.expander:
        print(f"Expander '{exp.label}' markdowns:", [el.value for el in getattr(exp, "markdown", [])])
    # Check all markdowns, including those in expanders
    all_markdowns = [el.value for el in app.markdown]
    for exp in app.expander:
        all_markdowns.extend(el.value for el in getattr(exp, "markdown", []))
    assert any("Mocked answer" in val for val in all_markdowns), "Answer not displayed"

def test_show_retrieved_context_expander(app, monkeypatch):
    monkeypatch.setattr(
        "sciencesage.main.retrieve_answer",
        lambda q, t, l: ("Mocked answer", ["Context A", "Context B"], [])
    )
    app.run()
    app.text_input[0].set_value("Test query")
    [b for b in app.button if b.label == "Get Answer"][0].click().run()
    expanders = [exp for exp in app.expander]
    print("Available expanders:", [exp.label for exp in expanders])
    expanders = [exp for exp in expanders if "Show retrieved context" in exp.label]
    assert expanders, "Context expander not found"
    expanders[0].is_open = True
    app.run()
    assert any("Context A" in el.value for el in getattr(expanders[0], "markdown", []))

def test_feedback_buttons_work(app, monkeypatch):
    monkeypatch.setattr(
        "sciencesage.main.retrieve_answer",
        lambda q, t, l: ("Mocked answer", [], [])
    )
    monkeypatch.setattr("sciencesage.main.save_feedback", lambda *a, **kw: None)
    app.run()
    app.text_input[0].set_value("Feedback test")
    [b for b in app.button if b.label == "Get Answer"][0].click().run()
    thumbs_up = [b for b in app.button if b.label == "👍"]
    thumbs_down = [b for b in app.button if b.label == "👎"]
    regen = [b for b in app.button if "Regenerate" in b.label]
    for btn in thumbs_up + thumbs_down + regen:
        btn.click().run()
        assert not app.exception, f"App crashed when clicking {btn.label}"

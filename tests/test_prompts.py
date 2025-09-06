from sciencesage.prompts import get_system_prompt, get_user_prompt

def test_system_prompt_varies_by_level():
    p1 = get_system_prompt("AI", "Middle School")
    assert "simple language" in p1
    p2 = get_system_prompt("AI", "Advanced")
    assert "in-depth" in p2

def test_user_prompt_contains_query_and_context():
    query = "What is AI?"
    ctx = "AI is the study of intelligent agents."
    result = get_user_prompt(query, ctx)
    assert query in result
    assert ctx in result

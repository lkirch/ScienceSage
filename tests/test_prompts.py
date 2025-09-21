from sciencesage.prompts import get_system_prompt, get_user_prompt
from loguru import logger

# -------------------------
# Logging
# -------------------------
logger.add("logs/test_prompts.log", rotation="5 MB", retention="7 days")
logger.info("Started test_prompts.py script.")

def test_system_prompt_varies_by_level():
    levels = ["Middle School", "College", "Advanced"]
    for level in levels:
        prompt = get_system_prompt("Space exploration", level)
        # Check that the prompt includes the level and the detail string for that level
        if level == "Middle School":
            assert "simple language" in prompt.lower() or "no jargon" in prompt.lower()
        elif level == "College":
            assert "undergraduates" in prompt.lower() or "technical terms" in prompt.lower()
        elif level == "Advanced":
            assert "graduate students" in prompt.lower() or "in-depth" in prompt.lower()
        assert level.lower() in prompt.lower()

def test_user_prompt_contains_query_context_and_level():
    query = "What are the main challenges of sending humans to Mars?"
    ctx = "Sending humans to Mars involves overcoming challenges such as radiation exposure, long-duration space travel, and landing safely on the Martian surface."
    level = "College"
    result = get_user_prompt(query, ctx, level)
    assert query in result
    assert ctx in result
    assert level.lower() in result.lower()

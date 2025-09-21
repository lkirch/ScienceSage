import pytest
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.config import LEVELS, TOPICS
from loguru import logger

# -------------------------
# Logging
# -------------------------
logger.add("logs/test_example_queries.log", rotation="5 MB", retention="7 days")
logger.info("Started test_example_queries.py script.")

# Example queries for current topics in config.py
example_queries = {
    "Space exploration": [
        "What are the main challenges of sending humans to Mars?",
        "How has space exploration advanced our understanding of the universe?"
    ],
    "Category:Space missions": [
        "What was the objective of the Voyager missions?",
        "Which space missions have explored the outer planets?"
    ],
    "Category:Discovery and exploration of the Solar System": [
        "How were the planets in our solar system discovered?",
        "What are the most important discoveries about the solar system in the last 50 years?"
    ],
    "Category:Exploration of Mars": [
        "What have we learned from the Mars rover missions?",
        "Why is Mars considered a candidate for future human colonization?"
    ],
    "Category:Exploration of the Moon": [
        "What did the Apollo missions discover about the Moon?",
        "What is the significance of water ice on the Moon?"
    ],
    "Animals in space": [
        "Why were animals sent into space before humans?",
        "Which animals have traveled the farthest from Earth?"
    ]
}

@pytest.mark.parametrize("topic,queries", example_queries.items())
@pytest.mark.parametrize("level", LEVELS)
def test_example_queries_generate_answers(topic, queries, level):
    for query in queries:
        answer, context, references = retrieve_answer(query, topic, level)
        assert isinstance(answer, str), f"No answer returned for {query} ({topic}, {level})"
        assert answer.strip() != "", f"Empty answer for {query} ({topic}, {level})"
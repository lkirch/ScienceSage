import pytest
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.config import LEVELS, TOPICS

# Example queries as in main.py
example_queries = {
    "AI": ["What is a neural network?", "Explain transformers."],
    "Climate": ["What is the greenhouse effect?", "How do solar panels work?"],
    "Space": ["How do black holes form?", "What is mimicry in animals?"],
}

@pytest.mark.parametrize("topic,queries", example_queries.items())
@pytest.mark.parametrize("level", LEVELS)
def test_example_queries_generate_answers(topic, queries, level):
    for query in queries:
        answer, context, references = retrieve_answer(query, topic, level)
        assert isinstance(answer, str), f"No answer returned for {query} ({topic}, {level})"
        assert answer.strip() != "", f"Empty answer for {query} ({topic}, {level})"
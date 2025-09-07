import pytest
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.config import LEVELS, TOPICS

# Example queries as in main.py
example_queries = {
    "Neuroplasticity": ["What is neuroplasticity?", "How do neurons rewire?"],
    "AI": ["What is a neural network?", "Explain transformers."],
    "Renewable Energy & Climate Change": ["What is the greenhouse effect?", "How do solar panels work?"],
    "Animal Adaptation": ["How do penguins stay warm?", "What is mimicry in animals?"],
    "Ecosystem Interactions": ["What is a food chain?", "How does deforestation affect biodiversity?"]
}

@pytest.mark.parametrize("topic,queries", example_queries.items())
@pytest.mark.parametrize("level", LEVELS)
def test_example_queries_generate_answers(topic, queries, level):
    for query in queries:
        answer, context, references = retrieve_answer(query, topic, level)
        assert isinstance(answer, str), f"No answer returned for {query} ({topic}, {level})"
        assert answer.strip() != "", f"Empty answer for {query} ({topic}, {level})"
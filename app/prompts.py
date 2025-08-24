"""
Prompt templates for the Scientific Concept Explainer.
"""

def get_system_prompt(topic: str, level: str) -> str:
    return f"You are a teacher explaining {topic} at a {level} level."

def get_user_prompt(query: str, context_text: str) -> str:
    return f"""
Question: {query}

Use the following retrieved context to guide your answer:
{context_text}

Please answer clearly, concisely, and at the appropriate level.
"""
"""
Prompt templates for the Scientific Concept Explainer.
"""

def get_system_prompt(topic: str, level: str) -> str:
    if level == "Middle School":
        detail = "Use simple language, analogies, and avoid jargon."
    elif level == "College":
        detail = "Use technical terms and provide detailed explanations suitable for undergraduates."
    elif level == "Advanced":
        detail = "Provide in-depth, technical, and nuanced explanations suitable for graduate students or professionals."
    else:
        detail = ""
    return f"You are a teacher explaining {topic} at a {level} level. {detail}"
    
def get_user_prompt(query: str, context_text: str) -> str:
    return f"""
Question: {query}

Use the following retrieved context to guide your answer:
{context_text}

Please answer clearly, concisely, and at the appropriate level.
"""
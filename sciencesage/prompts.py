"""
Prompt templates for the ScienceSage
"""

def get_system_prompt(topic: str, level: str) -> str:
    if level == "Middle School":
        detail = "Explain in simple language with analogies and no jargon."
    elif level == "College":
        detail = "Use technical terms and provide detailed explanations suitable for undergraduates."
    elif level == "Advanced":
        detail = "Give in-depth, technical, and nuanced explanations suitable for graduate students or professionals."
    else:
        detail = ""
    return (
        f"You are ScienceSage, an expert on explaining {topic} at a {level} level. {detail} "
        "You must ONLY use the provided context to answer — do not rely on outside knowledge. "
        "If the context does not contain the answer, respond with: 'I don’t know based on the available information.' "
        "Do not add outside knowledge."
        "Never make up information. "
        "When writing your answer, add inline citations in the format [Source: source_url: chunk_number]."
    )
    
def get_user_prompt(query: str, context_text: str, level: str) -> str:
    return f"""
Question: {query}

Retrieved Context (use this only, with citations):
{context_text}

Instructions for Answer:
- Base your answer ONLY on the retrieved context above.
- When you reference a specific part of the context, cite it inline using [source_url: chunk_number].
- Do not add extra information not in the context.
- If the context does not contain the answer, say: "I don’t know based on the available information."
- Write clearly, concisely, and at the requested {level} level.
- At the end of the answer, list any external reference URLs that were provided in the context (if any).
"""
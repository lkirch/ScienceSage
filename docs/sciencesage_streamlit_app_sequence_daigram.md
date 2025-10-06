## Streamlit App Sequence Diagram

The diagram below illustrates the end-to-end flow of a user query in ScienceSage:

[View the full sequence diagram](images/eraser_streamlit_app_sequence_diagram.png)

1. The user enters a question in the Streamlit UI.
2. The query is sent to the backend, which retrieves relevant documents using the retrieval system (Qdrant).
3. Retrieved documents are scored for relevance and passed to the LLM for answer generation.
4. The generated answer is returned to the user in the UI.
5. Users can submit feedback, which is stored and analyzed to update system metrics.

This sequence highlights the interaction between the user, frontend, backend, retrieval, LLM, and feedback components.
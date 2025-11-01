# Task 08 – Implement vector search logic

**Phase:** Internal Retrieval (RAG)

**Description:**

Implement a function to perform similarity search over the Qdrant vector store.  Given a user query, embed it using the same embedding model used for document chunks and query the vector database for the top‑K most similar passages.  Return a list of passages with their texts, metadata (document ID, chunk index) and similarity scores.  If necessary, allow filtering on metadata (e.g., by document type or user scope).

**Acceptance Criteria:**

* The search function embeds input queries consistently with the document embeddings.
* The function returns top‑K passages ranked by similarity score.
* Each returned passage includes text and metadata required for citation.
* Tests validate that relevant passages are retrieved for example queries and that edge cases (empty queries) are handled gracefully.

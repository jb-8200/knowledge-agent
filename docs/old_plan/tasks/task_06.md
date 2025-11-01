# Task 06 – Generate vector embeddings

**Phase:** Document Ingestion & Indexing

**Description:**

For each text chunk produced in Task 05, generate a fixed‑dimensional vector representation using a sentence‑transformer model (e.g., `all‑MiniLM‑L6‑v2`).  Use the `sentence-transformers` library or LangChain’s embedding wrappers.  Store the resulting embeddings and associated metadata in a Qdrant vector database.  Configure the vector store with an appropriate distance metric (e.g., cosine similarity) and collection schema.

**Acceptance Criteria:**

* Embeddings are generated for all chunks without errors.
* The Qdrant collection is created with fields for embeddings, document identifiers and metadata.
* Embeddings and metadata are persisted in Qdrant and can be retrieved via the client API.
* Tests verify that searching Qdrant with an example query returns expected passages.

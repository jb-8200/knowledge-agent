# Task 28 – Write backend unit and integration tests

**Phase:** Testing & Feedback

**Description:**

Develop a comprehensive test suite for the backend using `pytest`.  Create unit tests for each module: ingestion (file parsing, embedding generation), vector search, external search integration, summarization chains and critic chain.  Use fixtures to supply sample documents and queries.  Mock external services such as Firecrawl, Qdrant, search providers and the YouTube API to avoid network calls.  Write integration tests that spin up the FastAPI app using `TestClient` and verify end‑to‑end behavior (e.g., uploading a document and querying it).

**Acceptance Criteria:**

* The test suite covers major code paths and edge cases.
* All external dependencies are mocked to ensure deterministic tests.
* Integration tests verify that the API endpoints behave as expected.
* Tests can be run with `pytest` and pass without failures.

# Spec 28 – Write backend unit and integration tests

This specification outlines a testing strategy using `pytest`.

## Unit Tests

* Create a `tests/unit/` directory.
* Write test modules for each component:
  * `test_parsers.py` – test PDF, DOCX and Markdown parsing functions.
  * `test_chunking.py` – test chunk splitting logic for various text lengths.
  * `test_embeddings.py` – test that embedding generation returns expected vector shapes and no NaNs.
  * `test_retrieval.py` – test vector search using a small in‑memory Qdrant instance or a mocked client.
  * `test_search_tool.py` – mock the web search provider and test the search tool wrapper.
  * `test_synthesizer.py`, `test_external_summarizer.py`, `test_critic.py` – test the chains using stubbed LLM responses.
  * `test_memory.py` – test session creation, retrieval and clearing.
* Use fixtures to supply sample data and configure environment variables.

## Integration Tests

* Use FastAPI’s `TestClient` to spin up the app in memory.
* Test the following flows:
  * Upload a document, query it and verify the answer contains content from the document.
  * Query requiring external search and verify that external summaries are included.
  * Pin an answer and confirm that pinned notes are returned in subsequent responses.
  * Download a Markdown file and verify its content.
* Mock external services (Firecrawl, search provider, YouTube API) to return deterministic results.

## Running Tests

Install testing dependencies in `requirements.txt`:

```
pytest
pytest-mock
httpx
```

Run the test suite with:

```bash
pytest -q
```

Ensure that all tests pass before committing changes.

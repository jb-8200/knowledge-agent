# Task 02 – Create a `.env` file with configuration placeholders

**Phase:** Setup & Planning

**Description:**

Define a `.env` file to hold configuration variables for the backend.  Include keys required for the LLM provider (e.g., OpenAI, Anthropic, or another model service), the Qdrant instance, the web search provider and the YouTube Data API.  Leave placeholders for authentication tokens to be added later.

Suggested variables:

* `MODEL_PROVIDER_API_KEY` – API key for the chosen LLM service (or leave blank if running a local model).
* `QDRANT_URL` – URL for the Qdrant instance (e.g., `http://localhost:6333`).
* `SEARCH_API_KEY` – API key for the web search provider (e.g., Tavily or Serper).
* `YOUTUBE_API_KEY` – API key for the YouTube Data API.
* `FIRECRAWL_API_KEY` – API key for Firecrawl (if required) or leave blank for public usage.
* `AUTH_TOKEN_PLACEHOLDER` – reserved for future authentication implementation.

**Acceptance Criteria:**

* A `.env` file exists in the project root with the above keys defined (values may be placeholder strings).
* The `.env` file is excluded from version control via `.gitignore`.
* Environment variables can be loaded in a Python script using `python-dotenv` without raising a `KeyError`.

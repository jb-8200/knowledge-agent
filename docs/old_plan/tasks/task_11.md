# Task 11 – Prepare external search configuration

**Phase:** External Search Integration

**Description:**

Configure the external web search provider.  Choose a provider (e.g., Tavily, Serper, Google Custom Search) and obtain the necessary API key.  Add the key to the `.env` file as `SEARCH_API_KEY`.  Specify other configuration parameters such as API endpoint, max results and fallback behavior.  Write a small configuration module that reads these values from the environment and exposes them to the rest of the system.

**Acceptance Criteria:**

* The `.env` file contains a non‑empty `SEARCH_API_KEY` or an instructive placeholder.
* A configuration module reads and validates search configuration at startup.
* The search provider can be switched by changing environment variables without code changes.
* Unit tests cover configuration loading, missing keys and invalid settings.

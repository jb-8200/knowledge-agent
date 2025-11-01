# Task 13 – Summarize external snippets

**Phase:** External Search Integration

**Description:**

Implement a mechanism to condense raw search results into concise passages for the agent.  For each URL returned by the search tool, use Firecrawl to fetch and parse the page content.  Extract the main text and apply a summarization LLM chain to produce a short summary and a citation (the URL or a unique ID).  Combine multiple summaries into a structured list.  Optionally, deduplicate sources and remove irrelevant content.

**Acceptance Criteria:**

* The summarization function accepts a list of search results and returns a list of summaries with citations.
* Firecrawl is invoked to fetch page content and gracefully handles network errors and non‑HTML pages.
* The LLM chain produces succinct summaries that capture key facts from the source.
* Unit tests mock Firecrawl and LLM calls to validate summarization behavior and error handling.

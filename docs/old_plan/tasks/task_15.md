# Task 15 – Define the external summarizer chain

**Phase:** CAG Modules & Orchestration

**Description:**

Develop a LangChain `LLMChain` that summarizes external search results.  The chain should accept a list of summaries generated in Task 13 and produce a concise synthesis of the external information, preserving citations (URLs or IDs).  The output must clearly distinguish external sources from internal passages.  Design the prompt template to encourage the LLM to extract factual statements without introducing new content.

**Acceptance Criteria:**

* An LLM chain is defined with an appropriate prompt and model.
* The chain consumes a list of external summaries and produces a coherent combined summary with citations.
* The output clearly labels external information and avoids repeating internal content.
* Unit tests verify that the chain consolidates multiple summaries correctly and preserves citations.

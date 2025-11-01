# Task 17 – Compose the workflow

**Phase:** CAG Modules & Orchestration

**Description:**

Compose the retrieval tool, synthesizer chain, external search tool, external summarizer chain and critic chain into a coherent workflow.  Use conditional logic to determine whether to invoke external search based on the synthesizer’s `needs_external` flag.  This can be implemented using standard Python control flow or using LangChain’s experimental `langgraph` framework to define a stateful graph.  The workflow should accept a query and session context, perform retrieval, generate a draft answer, optionally call external search and summarization, and finally invoke the critic to produce the final answer and citations.

**Acceptance Criteria:**

* The workflow orchestrates the tools and chains in the correct order.
* External search is only triggered when the synthesizer indicates it is necessary.
* The workflow returns a structured response containing the final answer, citations, internal/external links, YouTube thumbnails (optional), related questions and any session updates.
* Integration tests simulate queries requiring internal and external knowledge and validate the response structure and content.

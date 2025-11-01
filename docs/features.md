# Feature Catalogue

> **📍 Navigation Note**: This document provides a quick feature reference with original task mapping.
> For **detailed feature specifications**, see `.work-items/{feature-name}/` directories (canonical source).
> For **task-to-feature mapping**, see `docs/migration/README.md`.

---

This document lists the core features of the knowledge‑base agent built with LangChain, Firecrawl and Qdrant.  Each feature corresponds to user‑visible functionality or a major capability required by the system.

| Feature | Description | Related Tasks |
|--------|-------------|---------------|
| **Document ingestion** | Users can upload PDF/Word/Markdown files or provide links.  The system parses, chunks and stores these documents along with their embeddings.  Firecrawl is used to fetch and parse web pages. | Tasks 03–07 |
| **Vector indexing (RAG)** | A Qdrant vector database holds embeddings of all passages.  Queries to the vector store return top‑K relevant passages with metadata. | Tasks 06–09 |
| **Retrieval‑augmented generation** | When answering a question, the system first consults the internal corpus using RAG to generate a draft answer grounded in the uploaded content. | Tasks 08–14 |
| **External web search** | If the internal corpus lacks sufficient information, the agent performs a live web search using a LangChain tool (e.g., Tavily or Serper).  Firecrawl then extracts page content for summarization. | Tasks 11–13 |
| **Critical reasoning and synthesis (CAG)** | Specialized LangChain chains (synthesizer, summarizer, critic) synthesize internal and external information, cross‑check facts and produce a coherent answer with citations. | Tasks 14–17 |
| **Session memory and continuity** | The system maintains conversation state across interactions, remembering previous queries, answers and pinned notes for better context. | Tasks 10, 23 |
| **Feedback capture** | Users can rate answers and provide comments.  Feedback is stored for offline evaluation and iterative improvement. | Task 30 |
| **HTML front‑end** | A simple search‑oriented web page with a white theme allows users to submit queries and view results.  It also displays citations, related documents, external links, YouTube thumbnails, similar questions and pinned notes. | Tasks 18–20 |
| **YouTube thumbnails** | The UI displays four thumbnails from YouTube videos related to the query.  These are retrieved via the YouTube Data API or a fallback. | Task 21 |
| **Similar questions list** | After answering, the system suggests up to five related questions that other users might ask. | Task 22 |
| **Pin answers** | Users can pin important answers, which then appear as short notes on the page; pinned answers persist across the session. | Task 23 |
| **Download as Markdown** | Users can download the answer, including citations, as a Markdown file. | Task 24 |
| **Deployable backend** | The system is designed to run locally during development but can be deployed to Firebase Hosting and Functions/Cloud Run or AWS ECS/Fargate for production. | Tasks 25–27 |
| **Automated testing & evaluation** | Unit, integration and UI tests verify functionality; feedback loops and evaluation frameworks measure and improve performance over time. | Tasks 28–30 |

| **Spec‑driven context and hooks** | The repository includes a `rules/` directory with core standards and a `.work-items/` directory of YAML tasks.  A bootstrap script and Claude Code hooks automatically load the rules, lint documentation and run tests before commits. | Tasks 31–35 |
| **Golden‑query evaluation harness** | A set of representative queries and expected key points are defined in `evals/golden-queries.yaml`.  A script or scheduled job runs these queries periodically and reports retrieval and citation quality. | Task 36 |
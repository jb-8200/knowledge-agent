# Project Scope

> **📍 Navigation Note**: This document provides a phase-based overview of the project scope.
> For **current implementation details**, see `.work-items/` directory (canonical source).
> This doc uses original task numbering (01-36) - see `docs/migration/` for task-to-feature mapping.

---

This document outlines the scope of the knowledge‑base agent built with LangChain, Firecrawl, and Qdrant.  Tasks are grouped into phases and expressed as granular, actionable items.

## Phases

| Phase | Description |
|------|-------------|
| **1. Setup & Planning** | Establish the development environment, install dependencies and prepare the base project structure.  Configure environment variables through a `.env` file. |
| **2. Document Ingestion & Indexing** | Develop services for uploading documents and links, parsing content, generating embeddings and storing both raw artifacts and vectors. |
| **3. Internal Retrieval (RAG)** | Create functions and tools that query the vector store to provide relevant passages with metadata and integrate them into the LangChain agent. |
| **4. External Search Integration** | Integrate a real‑time web search provider and Firecrawl for page retrieval, then summarize the returned snippets. |
| **5. CAG Modules & Orchestration** | Define LangChain chains for drafting answers, summarizing external snippets, and applying critical reasoning.  Compose them into a structured workflow (e.g., using LangGraph). |
| **6. User Interface** | Build a simple white‑themed HTML/CSS/JS front‑end that interacts with the backend and displays responses and related content. |
| **7. Additional Features** | Implement YouTube thumbnail retrieval, similar‑questions generation, pinning answers and downloading answers as markdown. |
| **8. Deployment** | Package the backend as a container and deploy it to Firebase Functions/Cloud Run or AWS ECS/Fargate with environment variables loaded from the `.env` file.  Leave placeholders for authentication. |
| **9. Testing & Feedback** | Create unit and integration tests, UI tests and user feedback capture mechanisms to support iterative improvement. |

| **10. Spec‑Driven Integration** | Integrate spec‑driven best practices by adding a rules directory, work‑item definitions, bootstrap scripts, linting configuration and evaluation harness.  These additions streamline development with Claude Code without altering the core agent architecture. |

## Features and Associated Tasks

### Phase 1 – Setup & Planning

| Task ID | Task description |
|---|---|
| **Task 01** | *Initialize the repository and virtual environment.*  Create the project directory, initialize a Git repository, and set up a Python virtual environment.  Install `langchain`, `firecrawl`, `qdrant-client`, `fastapi`, `uvicorn`, `python-dotenv`, `sentence-transformers` and other foundational dependencies. |
| **Task 02** | *Create a `.env` file with configuration placeholders.*  Define variables such as `MODEL_PROVIDER_API_KEY`, `QDRANT_URL`, `SEARCH_API_KEY`, `YOUTUBE_API_KEY` and placeholders for future authentication. |

### Phase 2 – Document Ingestion & Indexing

| Task ID | Task description |
|---|---|
| **Task 03** | *Implement a file upload endpoint.*  Provide a REST endpoint that accepts PDF, Word and Markdown files and forwards them to the ingestion service. |
| **Task 04** | *Implement a link ingestion endpoint.*  Provide a REST endpoint for submitting URLs; use Firecrawl to fetch the page content and forward it to the ingestion pipeline. |
| **Task 05** | *Parse and chunk uploaded documents.*  Use appropriate libraries (e.g., `pdfplumber`, `python-docx`, `markdown`) to extract text, split it into passages and normalize encoding. |
| **Task 06** | *Generate vector embeddings.*  Produce vector representations for each passage using a sentence‑transformer model and store them in a Qdrant vector database. |
| **Task 07** | *Persist original artifacts.*  Save the uploaded files and downloaded web pages in an artifact storage so they can be downloaded later. |

### Phase 3 – Internal Retrieval (RAG)

| Task ID | Task description |
|---|---|
| **Task 08** | *Implement vector search logic.*  Query Qdrant for the top‑K passages relevant to a query and return them with metadata including source identifiers. |
| **Task 09** | *Wrap the retrieval logic as a LangChain tool.*  Create a tool (using `Tool` or `StructuredTool`) that exposes the retrieval method so that it can be called within LangChain chains. |
| **Task 10** | *Configure session and memory services.*  Set up a session store and a conversation memory using either LangChain memory primitives or a custom data structure to maintain context across requests. |

### Phase 4 – External Search Integration

| Task ID | Task description |
|---|---|
| **Task 11** | *Prepare external search configuration.*  Obtain (or define placeholders for) an API key for a web search provider (e.g., Tavily, Serper) and configure environment variables. |
| **Task 12** | *Wrap the external search tool as a LangChain tool.*  Instantiate the search utility, wrap it into a LangChain `Tool` that accepts a query and returns search results (list of URLs/snippets). |
| **Task 13** | *Summarize external snippets.*  Implement logic to condense the raw search results into concise passages with associated citations using Firecrawl and an LLM chain. |

### Phase 5 – CAG Modules & Orchestration

| Task ID | Task description |
|---|---|
| **Task 14** | *Define the synthesizer chain.*  Create a LangChain `LLMChain` that drafts an answer solely from internal passages and indicates whether external information is needed. |
| **Task 15** | *Define the external summarizer chain.*  Create a LangChain `LLMChain` that summarizes external search results into structured information with citations. |
| **Task 16** | *Define the critic chain.*  Develop a LangChain `LLMChain` that merges internal and external summaries, resolves contradictions, and outputs a final answer with ordered citations. |
| **Task 17** | *Compose the workflow.*  Compose the retrieval tool, synthesizer, external search, external summarizer and critic into a structured workflow using LangChain chains or LangGraph to manage control flow based on whether external search is needed. |

### Phase 6 – User Interface

| Task ID | Task description |
|---|---|
| **Task 18** | *Design the HTML/CSS layout.*  Build a simple white‑theme search interface with sections for query input, answer display, citation list, internal/external links, YouTube thumbnails, follow‑up questions and pinned answers. |
| **Task 19** | *Implement client‑side API integration.*  Write JavaScript functions to send queries, feedback, pin actions and download requests to the backend and handle responses. |
| **Task 20** | *Render dynamic content.*  Populate the answer area, build citation lists, embed YouTube thumbnails, list related questions and display pinned notes based on the response payload. |

### Phase 7 – Additional Features

| Task ID | Task description |
|---|---|
| **Task 21** | *Retrieve YouTube thumbnails.*  Use the YouTube Data API (or a placeholder endpoint) to fetch four thumbnails relevant to the user’s query. |
| **Task 22** | *Generate similar questions.*  Call the LLM to produce up to five follow‑up questions that a user with a similar query might ask. |
| **Task 23** | *Implement pinning of answers.*  Allow users to click a pin icon next to an answer to save it as a short note on the side of the page; persist this in memory. |
| **Task 24** | *Implement download as Markdown.*  Convert the final answer and its citations into a Markdown file and return it for download. |

### Phase 8 – Deployment

| Task ID | Task description |
|---|---|
| **Task 25** | *Configure Firebase Hosting.*  Create configuration files (`firebase.json`, hosting configuration) and set up build scripts to deploy the static front‑end. |
| **Task 26** | *Deploy backend service.*  Package the Python backend (FastAPI + LangChain) into a Docker image and deploy it to Firebase Functions/Cloud Run or AWS ECS with environment variables loaded from the `.env` file. |
| **Task 27** | *Set up CORS and placeholders for authentication.*  Ensure cross‑origin requests are permitted between the front‑end and back‑end, and insert placeholder middleware for future authentication. |

### Phase 9 – Testing & Feedback

| Task ID | Task description |
|---|---|
| **Task 28** | *Write backend unit and integration tests.*  Develop tests for ingestion, embeddings, retrieval, external search and CAG chains using a testing framework. |
| **Task 29** | *Write UI tests.*  Create automated tests to verify the search interface, answer rendering, pinning and download features. |
| **Task 30** | *Implement feedback capture and evaluation.*  Build endpoints to record user ratings and comments and design a process to analyze this feedback (e.g., using RAG evaluation frameworks) to improve the system. |

### Phase 10 – Spec‑Driven Integration

| Task ID | Task description |
|---|---|
| **Task 31** | *Import `genai‑specs` and create rules directory.*  Add the `genai‑specs` repository as a submodule, copy or symlink the always‑included specification files into `rules/`, and document their purpose. |
| **Task 32** | *Set up work‑item YAML definitions.*  Create a `.work-items/` directory and add initial YAML files that map user stories to spec references, acceptance tests and code targets.  Use this to drive Claude Code sessions. |
| **Task 33** | *Write a bootstrap script for Claude Code.*  Implement `scripts/claude-init.sh` that verifies the submodule, seeds an `.env` file and prints a kickoff prompt instructing Claude to load the core rules. |
| **Task 34** | *Configure spec hygiene tooling.*  Add configuration files for Vale (`.vale.ini`) and Markdownlint (`.markdownlint-cli2.yaml`) and include them in the repository. |
| **Task 35** | *Implement Claude Code hooks.*  Create pre‑prompt, pre‑patch and pre‑commit hooks under `.claude/hooks/` to automatically load rules, lint documentation and run tests before committing. |
| **Task 36** | *Create evaluation harness.*  Add an `evals/` directory with `golden-queries.yaml` containing representative queries and expected key points.  Provide a script or instructions to run nightly evaluations and report regressions. |
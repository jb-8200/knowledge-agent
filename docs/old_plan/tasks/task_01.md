# Task 01 – Initialize the repository and virtual environment

**Phase:** Setup & Planning

**Description:**

Set up the basic development environment.  Create the project directory and initialise a Git repository.  Create a Python virtual environment, activate it, and install the core dependencies required for a LangChain‑based knowledge agent.  At minimum this includes `langchain`, `langgraph` (optional), `firecrawl`, `qdrant-client`, `sentence-transformers`, `fastapi`, `uvicorn`, `python-dotenv` and a search client (e.g., `tavily-python` or `serper`).  Verify that these packages import without errors.  Capture dependencies in a `requirements.txt` file to ensure repeatable installations.

**Acceptance Criteria:**

* A Git repository exists with an initial commit.
* A Python virtual environment is present and can be activated.
* The specified packages install successfully and can be imported in a Python REPL.
* A `requirements.txt` (or equivalent) lists the versions of installed dependencies.

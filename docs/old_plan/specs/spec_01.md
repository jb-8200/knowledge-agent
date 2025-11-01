# Spec 01 – Initialize the repository and virtual environment

This specification details the commands and structure required to initialize the project repository and prepare a Python development environment for a LangChain/Firecrawl/Qdrant knowledge agent.

## Repository Initialization

1. Create a new directory for the project and initialize Git:

   ```bash
   mkdir knowledge_agent && cd knowledge_agent
   git init
   ```

2. Add a `.gitignore` file to exclude the virtual environment, compiled Python files and environment files:

   ```gitignore
   __pycache__/
   venv/
   .env
   *.pyc
   artifacts/
   # Front‑end node modules if used
   node_modules/
   dist/
   ```

## Python Virtual Environment

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the foundational dependencies.  The core stack includes LangChain for composing LLM chains, Firecrawl for web page extraction, Qdrant client for vector operations, FastAPI and Uvicorn for the server, and python‑dotenv to load environment variables:

   ```bash
   pip install langchain langgraph firecrawl qdrant-client fastapi uvicorn python-dotenv sentence-transformers tavily-python tenacity
   ```

3. Verify installation by importing the key libraries in a Python shell:

   ```python
   >>> import langchain, firecrawl, qdrant_client, fastapi
   >>> print(langchain.__version__)
   ```

4. Freeze dependencies into `requirements.txt` for deployment:

   ```bash
   pip freeze > requirements.txt
   ```

## Directory Structure

After initialization, the repository should have the following structure:

```
knowledge_agent/
├── app/                # Python backend code (FastAPI application)
├── frontend/           # HTML/CSS/JS files
├── ingestion/          # Document ingestion and vector store modules
├── tests/              # Backend unit/integration tests
├── tasks/              # Task descriptions
├── specs/              # Technical specifications
├── acceptance_tests/   # Acceptance test descriptions
├── requirements.txt
├── .env                # Environment variables (not committed)
└── README.md
```

# Acceptance Test for Task 01 – Initialize the repository and virtual environment

**Objective:** Ensure that the repository is initialized correctly and that required packages install and import without errors.

**Test Steps:**

1. Run the repository initialization steps: create the project directory, run `git init` and create a Python virtual environment.
2. Install the specified packages (`langchain`, `langgraph`, `firecrawl`, `qdrant-client`, `fastapi`, `uvicorn`, `python-dotenv`, `sentence-transformers`, `tavily-python`).
3. Start a Python REPL and attempt to import each installed package.
4. Generate a `requirements.txt` file using `pip freeze`.

**Expected Result:**

* The Git repository is created and contains an initial commit.
* The virtual environment activates without errors.
* All specified packages import successfully in the Python REPL.
* `requirements.txt` lists the installed dependencies.

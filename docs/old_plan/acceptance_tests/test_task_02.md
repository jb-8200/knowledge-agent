# Acceptance Test for Task 02 – Create a `.env` file with configuration placeholders

**Objective:** Verify that the `.env` file is created with the correct keys and that environment variables can be loaded.

**Test Steps:**

1. Create a `.env` file in the project root containing keys: `MODEL_PROVIDER_API_KEY`, `QDRANT_URL`, `SEARCH_API_KEY`, `YOUTUBE_API_KEY`, `FIRECRAWL_API_KEY`, `AUTH_TOKEN_PLACEHOLDER`.
2. Ensure that `.env` is listed in `.gitignore`.
3. In a Python script, call `load_dotenv()` and retrieve each variable using `os.environ.get()`.
4. Assign dummy values to the variables and ensure they are loaded correctly.

**Expected Result:**

* The `.env` file exists and includes all required keys.
* The `.env` file is ignored by Git.
* Environment variables are loaded and available in the application without raising errors.

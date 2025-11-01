# Acceptance Test for Task 11 – Prepare external search configuration

**Objective:** Verify that the environment variables and configuration for the external search provider are set correctly.

**Test Steps:**

1. Check the `.env` file for the presence of `TAVILY_API_KEY` or the appropriate external search API key.
2. Run the backend application and inspect the configuration loader to ensure it reads the search API key from the environment and does not hard‑code it.
3. Attempt to perform a search using the configured key; if the API returns an authentication error, update the key and retest.
4. Confirm that the application logs meaningful error messages when the key is missing or invalid, without causing unhandled exceptions.

**Expected Result:** The external search API key is configurable via the environment, loaded correctly and validated at runtime; missing or invalid keys produce informative logs.

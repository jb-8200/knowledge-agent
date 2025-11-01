# Acceptance Test for Task 26 – Deploy backend service

**Objective:** Ensure that the Python backend is packaged and deployed successfully to Firebase Functions or Cloud Run.

**Test Steps:**

1. Verify that a `requirements.txt` file lists all dependencies, including `langchain`, `langgraph`, `firecrawl`, `qdrant-client`, `fastapi`, `uvicorn`, `python-dotenv`, `sentence-transformers`, `tavily-python` (or equivalent search client) and test libraries.
2. Confirm that a deployment configuration (`firebase.json` functions section, or `Dockerfile` for Cloud Run) exists specifying the entry point (`main.py`) and runtime.
3. Deploy the backend using the Firebase CLI (`firebase deploy --only functions`) or Cloud Run CLI (`gcloud run deploy`).
4. After deployment, send a test request to the deployed endpoint (e.g., via `curl`) and verify that the backend responds correctly to `/query` and other endpoints.
5. Check that environment variables from the `.env` file are available in the deployed environment through Firebase config or secrets.

**Expected Result:** The backend service deploys without errors, endpoints are reachable, and environment variables are securely loaded.

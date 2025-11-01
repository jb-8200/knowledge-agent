# Task 26 – Deploy backend service

**Phase:** Deployment

**Description:**

Package the Python backend (FastAPI + LangChain) as a container or zip that can run on Firebase Functions, Cloud Run or AWS ECS.  Define a `Dockerfile` or runtime configuration that installs dependencies, copies the source code, sets environment variables and launches the FastAPI app with `uvicorn`.  Configure build and deployment scripts for the chosen platform.  Load environment variables from a secure source (e.g., Google Secret Manager or AWS Secrets Manager) rather than shipping `.env` in the container.  Validate that the deployed service can handle queries and return responses within acceptable latency.

**Acceptance Criteria:**

* A reproducible build configuration (e.g., `Dockerfile`) exists and builds the backend image successfully.
* The service runs on the chosen platform with environment variables correctly injected.
* Health checks and basic queries return expected responses in the deployed environment.
* Deployment scripts (Firebase `functions.yaml`, `gcloud run deploy`, or ECS task definition) are present and documented.

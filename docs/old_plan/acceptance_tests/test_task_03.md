# Acceptance Test for Task 03 – Implement a file upload endpoint

**Objective:** Ensure that the `POST /upload/file` endpoint accepts valid documents and initiates ingestion.

**Test Steps:**

1. Start the FastAPI application.
2. Using an HTTP client (e.g., `httpx` or Postman), send a `POST` request to `/upload/file` with a sample PDF, DOCX and Markdown file in separate test cases.
3. Verify that the response has status code 200 and includes an `ingestion_id` or status message.
4. Attempt to upload an unsupported file type (e.g., `.exe`) and verify that the endpoint returns a 400 error.
5. Check that the ingestion function is enqueued or called (e.g., by inspecting logs or using a mock ingestion function in tests).

**Expected Result:**

* Supported file types are accepted, and the response confirms receipt.
* Unsupported file types return a 4xx error.
* The ingestion pipeline is triggered for valid uploads.

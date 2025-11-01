# Acceptance Test for Task 04 – Implement a link ingestion endpoint

**Objective:** Ensure that the `POST /upload/link` endpoint validates URLs and triggers Firecrawl-based ingestion.

**Test Steps:**

1. Start the FastAPI application with the `fetch_and_ingest_link` function mocked.
2. Send a `POST` request to `/upload/link` with a valid URL in the JSON payload.
3. Verify that the response has status code 200 and includes an `ingestion_id`.
4. Confirm that the mock `fetch_and_ingest_link` function is called with the correct URL and ingestion ID.
5. Send a request with an invalid URL and verify that FastAPI returns a 422 validation error.

**Expected Result:**

* Valid URLs are accepted and processed.
* Invalid URLs result in a validation error.
* The ingestion function is invoked with the correct parameters for valid inputs.

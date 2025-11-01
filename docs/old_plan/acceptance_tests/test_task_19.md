# Acceptance Test for Task 19 – Implement client‑side API integration

**Objective:** Verify that the front‑end communicates with the backend via REST endpoints and handles responses correctly.

**Test Steps:**

1. Open the web page and enter a query; trigger the search function.
2. Inspect the network tab of browser developer tools and confirm that a `POST` request is sent to the `/query` endpoint with the query payload.
3. Verify that the response is parsed by the JavaScript code and populates the answer, citations, related documents, external links, thumbnails and similar questions.
4. Trigger pin and download actions and ensure that appropriate requests are sent to `/pin` and `/download` endpoints.
5. Submit feedback via the UI and check that it is sent to `/feedback`.

**Expected Result:** Client‑side code correctly constructs and sends API requests, handles responses without errors, and updates the DOM accordingly.

# Task 19 – Implement client‑side API integration

**Phase:** User Interface

**Description:**

Write JavaScript functions to communicate with the backend.  Create a helper function to send JSON requests (using `fetch`) to endpoints such as `/query`, `/feedback`, `/pin` and `/download`.  For queries, send the user’s question and session ID (if available) and handle streaming or standard responses.  Implement error handling for network issues and display user‑friendly messages.  Ensure that feedback, pinning and download actions trigger the appropriate API calls and update the UI state accordingly.

**Acceptance Criteria:**

* API requests are sent using `fetch` with proper headers and payloads.
* The query function handles asynchronous responses and updates the answer area.
* Feedback, pin and download functions call their respective endpoints and reflect changes in the UI.
* Tests using a mock server validate the correctness of API interactions and error handling.

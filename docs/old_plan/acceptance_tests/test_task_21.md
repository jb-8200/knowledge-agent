# Acceptance Test for Task 21 – Retrieve YouTube thumbnails

**Objective:** Verify that the backend retrieves and returns up to four YouTube thumbnail URLs related to the query.

**Test Steps:**

1. Send a query known to yield YouTube search results (e.g., “machine learning tutorial”).
2. Check the response payload for a list of up to four thumbnail URLs and video IDs.
3. In the browser, ensure that these URLs display the corresponding images when rendered.
4. Simulate API quota exhaustion or invalid API keys and confirm that the service falls back to a default placeholder image and logs an informative message.
5. Verify that the YouTube API key is read from the environment and not hard‑coded in the code base.

**Expected Result:** For valid queries and keys, the backend returns up to four valid thumbnail URLs; on failure, it returns placeholder images without crashing.

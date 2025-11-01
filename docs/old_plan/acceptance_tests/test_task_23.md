# Acceptance Test for Task 23 – Implement pinning of answers

**Objective:** Confirm that users can pin answers and that pinned notes appear as single‑line summaries on the right side of the page.

**Test Steps:**

1. After receiving an answer, click the pin icon associated with it.
2. Observe that a short summary of the answer appears in the pinned notes section; it should include the query text or truncated answer.
3. Reload the page or perform another query and verify that the pinned note persists within the current session.
4. Attempt to unpin or remove a pinned note (if supported) and ensure it disappears from the list.
5. Confirm that pinned answers are stored in session memory rather than in the main data store.

**Expected Result:** Pinning an answer creates a persistent summary in the pinned area for the duration of the session, and removing it clears the note.

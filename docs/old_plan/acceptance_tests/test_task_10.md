# Acceptance Test for Task 10 – Configure session and memory services

**Objective:** Validate that the system maintains conversation context across user interactions using session memory and a custom session store (e.g., Redis or an in‑memory dictionary).

**Test Steps:**

1. Start a new session and ask a question via the UI or API.
2. Confirm that the response includes memory updates (e.g., stored query, answer and citations) in the session store.
3. Ask a follow‑up question that refers to previous context (e.g., “What about its drawbacks?”) and verify that the agent uses the stored context to answer appropriately.
4. Inspect the memory or session store (e.g., by reading the in‑memory structure or Redis) to ensure that both queries and answers are recorded.
5. End the session and start a new one; confirm that the previous session’s memory does not leak into the new session.

**Expected Result:** The system stores session context and uses it for follow‑up questions while isolating sessions properly.

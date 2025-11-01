# Acceptance Test for Task 22 – Generate similar questions

**Objective:** Ensure that the LLM generates up to five follow‑up questions based on the original query.

**Test Steps:**

1. After submitting a query, capture the list of “People with similar question also asked” questions returned by the backend.
2. Confirm that there are no more than five questions and that they are semantically related to the original query.
3. Evaluate the quality of these questions: they should be phrased coherently and inspire logical follow‑ups.
4. Click a generated question and verify that it is sent as a new query, resulting in a fresh answer.
5. Test multiple topics to ensure the LLM consistently produces reasonable follow‑up questions.

**Expected Result:** The system proposes up to five relevant follow‑up questions for each query and supports using them as new queries.

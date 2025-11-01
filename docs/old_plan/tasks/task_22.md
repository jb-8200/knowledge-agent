# Task 22 – Generate similar questions

**Phase:** Additional Features

**Description:**

After answering a query, produce up to five related questions that other users might ask.  Implement a function that calls an LLM chain with a prompt instructing it to generate follow‑up questions based on the user’s original query.  Ensure that the questions are distinct and relevant.  Optionally, include context from the current conversation to tailor the suggestions.

**Acceptance Criteria:**

* The function accepts the user’s query (and optionally context) and returns a list of up to five questions.
* Generated questions are relevant to the original topic and are unique.
* The questions do not include the answer content or reveal internal citations.
* Unit tests verify that the function produces non‑empty results for typical inputs and handles empty or null queries gracefully.

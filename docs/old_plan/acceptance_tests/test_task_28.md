# Acceptance Test for Task 28 – Write backend unit and integration tests

**Objective:** Validate the quality and coverage of backend unit and integration tests.

**Test Steps:**

1. Run `pytest` in the project root and ensure that all unit and integration tests execute without failures.
2. Review the test coverage report (e.g., using `pytest --cov`) and verify that the coverage meets or exceeds the target threshold (e.g., 80%).
3. Inspect several representative unit tests to confirm that they include both typical and edge cases (e.g., missing files, invalid inputs).
4. Examine integration tests to ensure they simulate real workflows, including ingestion, retrieval, external search, synthesis, criticism and feedback submission.
5. Confirm that external services (YouTube, Tavily) are mocked appropriately and that tests do not make network calls.

**Expected Result:** The backend test suite runs cleanly with high coverage, comprehensive test cases and no external dependencies.

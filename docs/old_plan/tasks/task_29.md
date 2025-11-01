# Task 29 – Write UI tests

**Phase:** Testing & Feedback

**Description:**

Use Playwright or another modern browser automation framework to write end‑to‑end tests for the user interface.  Tests should cover basic interactions such as entering a query, receiving and displaying an answer, clicking citations, pinning an answer, downloading as Markdown and navigating to follow‑up questions.  Ensure that the UI behaves correctly across different screen sizes.  Include tests for error scenarios (e.g., network failure) and verify that fallback messages appear.

**Acceptance Criteria:**

* The Playwright test suite launches the application and executes the core user flows.
* Assertions verify that elements appear with the expected text and that user interactions produce the correct API calls and UI updates.
* Tests are run in headless mode and pass without timing failures.
* A GitHub Action or equivalent pipeline step executes the UI tests automatically.

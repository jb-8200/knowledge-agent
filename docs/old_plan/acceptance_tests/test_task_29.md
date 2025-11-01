# Acceptance Test for Task 29 – Write UI tests

**Objective:** Confirm the robustness of automated UI tests for the front‑end.

**Test Steps:**

1. Execute the UI test suite using the chosen framework (e.g., `npm run test` for Jest or `npx playwright test`).
2. Review test logs to ensure that the tests cover major user interactions: submitting queries, viewing answers, pinning, downloading and navigating follow‑up questions.
3. Validate that tests run headlessly, can be integrated into CI pipelines and complete within reasonable time limits.
4. Inspect accessibility tests (if any) for compliance with WCAG guidelines, verifying labels, ARIA attributes and color contrast.
5. Introduce a deliberate change (e.g., remove a label) and confirm that the failing test detects the issue.

**Expected Result:** The UI tests execute successfully, cover essential interactions, enforce accessibility and catch regressions.

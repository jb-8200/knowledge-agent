# Task 23 – Implement pinning of answers

**Phase:** Additional Features

**Description:**

Allow users to pin important answers so they appear as brief notes on the side of the page.  Implement a backend endpoint `POST /pin` that accepts an answer ID and an optional summary.  Store pinned answers in the session memory along with their question, a short snippet of the answer and timestamp.  In the UI, display pinned notes in a dedicated sidebar.  Provide functionality to unpin items as well.

**Acceptance Criteria:**

* The `/pin` endpoint accepts a valid answer ID, stores the pinned note and returns a success response.
* Pinned answers persist across the session and are included in subsequent responses.
* The UI displays pinned notes and updates when new answers are pinned or unpinned.
* Tests verify that pinning and unpinning operations update session memory and that pinned notes are returned with responses.

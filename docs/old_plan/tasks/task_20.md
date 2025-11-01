# Task 20 – Render dynamic content

**Phase:** User Interface

**Description:**

Create functions to populate the UI with data returned from the backend.  When the user submits a query, clear previous results and display loading indicators.  Once the response arrives, update the answer section with formatted text and numbered citations.  Generate lists of internal document links and external URLs from the `citations` and `external_links` fields.  Embed YouTube thumbnails with clickable links to the videos.  Display the list of follow‑up questions and provide a way to ask them.  Show pinned notes on the right, and highlight newly pinned answers.  Manage state updates gracefully when the user refreshes or submits a new query.

**Acceptance Criteria:**

* The UI updates dynamically based on the backend response structure.
* Citations link to the correct internal or external resources.
* YouTube thumbnails load from the provided URLs and are clickable.
* Follow‑up questions appear as clickable items that trigger new queries.
* Pinned notes are displayed and updated when the user pins or unpins an answer.
* Manual tests confirm the UI behaves correctly across multiple interactions.

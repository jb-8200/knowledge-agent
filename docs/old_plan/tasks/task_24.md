# Task 24 – Implement download as Markdown

**Phase:** Additional Features

**Description:**

Provide the ability for users to download the final answer and its citations as a Markdown file.  Create a backend endpoint `GET /download/{answer_id}` that retrieves the answer and citation information from session memory or the artifact store, formats it into Markdown (including headings, paragraphs and a references list) and returns it with an appropriate `Content-Type` header (`text/markdown`).  In the UI, add a button that triggers this download for the current answer.

**Acceptance Criteria:**

* The download endpoint returns a well‑structured Markdown file containing the answer and numbered citations.
* The file includes a references section with links to internal documents (by ID or file name) and external URLs.
* The UI provides a clickable download button that triggers the endpoint and prompts the user to save the file.
* Unit tests verify Markdown formatting and correct inclusion of citations.

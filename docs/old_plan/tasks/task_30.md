# Task 30 – Implement feedback capture and evaluation

**Phase:** Testing & Feedback

**Description:**

Create endpoints and processes for capturing user feedback and evaluating system performance.  Implement a `POST /feedback` endpoint that accepts a rating (e.g., 1–5 stars) and an optional comment.  Store feedback in a database or file system associated with the corresponding answer and user session.  Design a routine to analyze feedback data and compute metrics such as average rating per answer, common issues or improvement suggestions.  Optionally, integrate a RAG evaluation framework (e.g., RAGAS) to automatically score answers based on recall and faithfulness.

**Acceptance Criteria:**

* The feedback endpoint records ratings and comments without exposing sensitive user data.
* Feedback can be retrieved and aggregated for offline analysis.
* A basic evaluation script computes summary statistics from feedback data.
* Tests validate that feedback submission and retrieval work correctly and that evaluation metrics are computed without errors.

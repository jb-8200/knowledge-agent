# Acceptance Test for Task 08 – Implement vector search logic

**Objective:** Ensure that the vector search function returns the most relevant passages with metadata.

**Test Steps:**

1. Populate a Qdrant collection with a small set of known passages and their embeddings.
2. Call the search function with a query known to match one of the passages.
3. Verify that the top result corresponds to the expected passage and that its metadata (e.g., document ID) is present.
4. Call the search function with an unrelated query and verify that the returned list is empty or has low scores.
5. Test the function with an empty string query and ensure it returns an empty list or a controlled response.

**Expected Result:**

* Relevant passages are ranked highest and include metadata and scores.
* Irrelevant queries return an empty or low‑scoring result set.
* The function handles edge cases gracefully.

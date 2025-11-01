# Acceptance Test for Task 06 – Generate vector embeddings

**Objective:** Ensure that embeddings are generated for text chunks and stored in Qdrant correctly.

**Test Steps:**

1. Prepare a small list of text chunks (e.g., 3 strings).
2. Call the embedding function to obtain vectors and verify that each vector has the expected dimension (e.g., 384 for MiniLM).
3. Use the Qdrant client to create a test collection and upload the vectors with payload metadata.
4. Query the test collection for one of the texts and verify that the correct vector is returned as the top result.
5. Clean up the test collection after the test.

**Expected Result:**

* Vectors are generated with the correct shape and no NaNs.
* Qdrant stores the vectors and metadata correctly.
* Similarity search retrieves the expected chunk as the top match.

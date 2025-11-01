# Acceptance Test for Task 07 – Persist original artifacts

**Objective:** Verify that uploaded files and web pages are saved in the artifact store with correct metadata.

**Test Steps:**

1. Simulate an upload by saving a temporary file and calling the `save_upload` function.
2. Verify that the file is moved to the `artifacts/uploads/` directory and that a metadata file is created with a `.meta.json` extension.
3. Check that the metadata includes the original filename, MIME type, upload time and vector IDs.
4. Use the artifact ID to retrieve the file and metadata via the download endpoint (see Task 24).

**Expected Result:**

* Files are saved under the `artifacts` directory with a unique identifier.
* Metadata JSON files exist and contain the required fields.
* The download endpoint returns the correct file and metadata when requested.

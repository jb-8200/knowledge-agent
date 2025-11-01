# Acceptance Test for Task 24 – Implement download as Markdown

**Objective:** Ensure that users can download answers as Markdown files with citations preserved.

**Test Steps:**

1. After receiving a final answer, click the “Download as MD” button.
2. Check that the browser downloads a `.md` file with a unique filename.
3. Open the downloaded file and verify that it contains the answer text, numbered citations with their corresponding URLs and a timestamp.
4. Confirm that the file is saved in the artifact store and associated with the correct session or query.
5. Attempt to download multiple answers and ensure each file has a unique identifier to avoid overwriting.

**Expected Result:** The download function produces correctly formatted Markdown files containing the answer and citations, stores them and triggers browser download.

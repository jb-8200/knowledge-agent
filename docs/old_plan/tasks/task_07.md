# Task 07 – Persist original artifacts

**Phase:** Document Ingestion & Indexing

**Description:**

Store uploaded files and downloaded web pages in a persistent artifact store for future retrieval and download.  For local development, this can be a directory structure (`artifacts/`) with subfolders grouped by upload date or user session.  Each artifact should be saved with a unique identifier and metadata including original filename, upload timestamp, MIME type and a link to the corresponding vector entries.  When deployed, map the artifact store to a cloud storage bucket (e.g., Firebase Storage or S3).

**Acceptance Criteria:**

* Uploaded documents and crawled pages are saved to the artifact store with unique IDs and metadata.
* A mapping exists between vector store entries and their original artifacts.
* The system exposes an endpoint to download raw artifacts by ID.
* Unit tests verify that artifacts are saved, retrieved and linked correctly.

# Task 03 – Implement a file upload endpoint

**Phase:** Document Ingestion & Indexing

**Description:**

Create a REST endpoint `POST /upload/file` using FastAPI that accepts multipart/form‑data uploads of PDF, Word and Markdown files.  Upon receiving a file, the endpoint should validate the file type, save the file to a temporary location and enqueue it for ingestion.  The ingestion service will parse and chunk the document, generate embeddings and store both raw artifacts and vectors.  Return a JSON response indicating that the file has been received and is being processed.

**Acceptance Criteria:**

* The endpoint accepts supported file types and returns a 4xx error for unsupported types.
* Uploaded files are stored temporarily and forwarded to the ingestion pipeline.
* The response includes an `ingestion_id` or status message confirming receipt.
* Unit tests simulate file uploads and verify that the ingestion service is triggered.

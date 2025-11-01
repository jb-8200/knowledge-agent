# Task 04 – Implement a link ingestion endpoint

**Phase:** Document Ingestion & Indexing

**Description:**

Provide a REST endpoint `POST /upload/link` that accepts a JSON payload containing a URL.  Validate the URL format and use Firecrawl to fetch and parse the web page content asynchronously.  Save the raw HTML and extracted text as artifacts, then pass the extracted text to the ingestion pipeline for chunking and embedding.  Return a response with an `ingestion_id` or status indicating that the link is being processed.

**Acceptance Criteria:**

* Invalid URLs are rejected with an appropriate error message.
* Valid URLs trigger an asynchronous Firecrawl fetch and ingestion.
* The response confirms receipt and processing of the link.
* Unit tests mock Firecrawl requests and verify the pipeline is invoked.

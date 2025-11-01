# User Story: Document Ingestion

## User Persona

**Name:** Research Analyst

**Description:** A knowledge worker who regularly consumes research papers, technical documentation, web articles, and reports. They need to build a searchable knowledge base from diverse sources (PDFs, Word documents, web pages) to quickly find relevant information across all their materials.

## Story

**As a** Research Analyst
**I want to** upload documents and provide web links to be processed and indexed
**so that** I can search across all my sources to find answers and connections between different materials

## Acceptance Criteria (EARS Format)

- WHEN I upload a PDF, DOCX, or Markdown file THEN I SHALL receive confirmation with an ingestion ID
- WHEN I submit a URL for ingestion THEN I SHALL see the system fetch and process the web page content
- IF I upload an unsupported file type THEN I SHALL receive a clear error message indicating which types are supported
- WHEN a document is processed THEN I SHALL see it parsed into searchable chunks with preserved metadata
- WHEN chunks are created THEN I SHALL see each chunk converted to a vector embedding and stored in Qdrant
- WHEN I upload a file THEN I SHALL have the original artifact saved for future retrieval
- IF a web page cannot be fetched THEN I SHALL receive an error message without system failure
- WHEN ingestion completes THEN I SHALL be able to search the indexed content via vector similarity

## Success Metrics

- ✅ File upload endpoint accepts PDF, DOCX, and Markdown files
- ✅ URL ingestion endpoint validates and fetches web content via Firecrawl
- ✅ Parsers extract text from all supported formats without errors
- ✅ Chunking produces passages of 500-1500 characters with 200 character overlap
- ✅ All chunks generate 384-dimensional embeddings (MiniLM model)
- ✅ Embeddings persist to Qdrant with complete metadata (filename, chunk_index, source)
- ✅ Original files and web pages saved to artifacts directory with metadata
- ✅ Vector search retrieves relevant chunks with >0.7 similarity score

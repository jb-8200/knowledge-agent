# User Story: External Search Integration

## User Persona

**Name:** Research Analyst

**Description:** A professional researcher who needs comprehensive answers that may require information beyond their uploaded documents. They value accuracy and want to know when answers include external sources.

## Story

**As a** Research Analyst
**I want to** automatically search the web when my knowledge base lacks information
**so that** I can get complete answers without manually searching external sources

## Acceptance Criteria (EARS Format)

- WHEN my knowledge base lacks sufficient information THEN I SHALL see the system automatically search external sources
- WHEN external sources are used THEN I SHALL see clear citations distinguishing them from internal documents
- WHEN I review an answer THEN I SHALL see which parts came from my documents vs. the web
- IF external search fails THEN I SHALL still receive an answer based on internal knowledge
- WHEN external content is retrieved THEN I SHALL see it properly summarized and cited

## Success Metrics

- ✅ External search triggers only when internal knowledge is insufficient
- ✅ Web search returns relevant results for queries
- ✅ Firecrawl successfully extracts content from result URLs
- ✅ External citations are clearly marked (e.g., [E1], [E2])
- ✅ Answers distinguish internal vs. external information

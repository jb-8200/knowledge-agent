# Task Breakdown: External Search Integration

## Overview

Integrate web search and content extraction to supplement internal knowledge base when needed.

## Requirements Traceability

- Links to: `user-story.md` - Research Analyst needs comprehensive answers
- Links to: `design.md` - Search service, Firecrawl, tool wrapper
- Original tasks: Task 11, Task 12, Task 13
- Dependencies: F05 (ExternalSummarizer chain)

## Test Strategy

- **Unit Tests**: Search API calls, Firecrawl extraction, tool invocation
- **Integration Tests**: End-to-end search → extract → summarize
- **Mocking**: Use VCR or responses library for API calls

## Sequential Steps

### 01 - Configure Search Service (Task 11)
- Set up Tavily API client
- Add configuration to .env
- Test search queries
**Time**: 1-2 hours

### 02 - Implement Search Tool Wrapper (Task 12)
- Create ExternalSearchTool as LangChain StructuredTool
- Integrate Firecrawl for content extraction
- Add retry logic and error handling
**Time**: 2-3 hours

### 03 - Integrate Content Summarization (Task 13)
- Use ExternalSummarizer from F05
- Combine search + extraction + summarization
- Test complete pipeline
**Time**: 2-3 hours

## Commit Strategy

- Commit 1: Add search service configuration
- Commit 2: Implement search tool with Firecrawl
- Commit 3: Integrate summarization pipeline

## Dependencies

- F05: ExternalSummarizer chain must exist
- Tavily API key configured
- Firecrawl API key configured

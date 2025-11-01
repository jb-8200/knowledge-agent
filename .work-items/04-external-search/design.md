# Design: External Search Integration

## Objective

Enable automatic web search and content extraction when internal knowledge base lacks sufficient information, with clear citation of external sources.

## Technical Design

### System Architecture

External search integrates into the answer synthesis pipeline:

1. **Synthesizer** indicates `needs_external=true`
2. **Search Tool** queries web search API (Tavily/Serper)
3. **Firecrawl** extracts full content from result URLs
4. **Summarizer** condenses external content with citations
5. **Critic** merges internal and external information

### Components

- **SearchService**: Web search API integration
- **ExternalSearchTool**: LangChain tool wrapper
- **ContentExtractor**: Firecrawl integration for page retrieval
- **ExternalSummarizer**: LLM chain for summarizing web content (from F05)

## Key Changes

### 3.1 API Contracts

**External Search Tool** (internal LangChain tool):
```python
Input: {
  "query": str,
  "max_results": int  # default: 5
}

Output: {
  "results": [
    {
      "title": str,
      "url": str,
      "snippet": str,
      "content": str  # from Firecrawl
    }
  ]
}
```

### 3.2 Data Models

```python
class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class SearchResult(BaseModel):
    title: str
    url: HttpUrl
    snippet: str
    content: Optional[str]  # Full page content

class ExternalSearchResponse(BaseModel):
    results: List[SearchResult]
    search_time_ms: int
```

### 3.3 Component Responsibilities

**SearchService**:
- Configure search API (Tavily recommended)
- Execute web searches
- Handle rate limits and errors
- Return top-K results

**ContentExtractor**:
- Initialize Firecrawl client
- Fetch full page content for each URL
- Handle extraction failures gracefully
- Apply content length limits

**ExternalSearchTool**:
- Wrap SearchService + ContentExtractor
- Expose as LangChain StructuredTool
- Integrate with workflow orchestrator
- Cache results per session

## Technology Stack

- **Tavily API**: Web search (recommended for AI applications)
- **Firecrawl**: Web scraping and content extraction
- **LangChain**: Tool framework and orchestration
- **Tenacity**: Retry logic for API calls

## Configuration

```python
# .env additions
SEARCH_PROVIDER=tavily  # or 'serper', 'google'
SEARCH_API_KEY=your_tavily_key
FIRECRAWL_API_KEY=your_firecrawl_key

# Search limits
MAX_SEARCH_RESULTS=5
MAX_CONTENT_LENGTH=10000  # chars per page
SEARCH_TIMEOUT=10  # seconds
```

## Alternatives Considered

1. **Search Provider**: Tavily (AI-optimized) vs. Serper (Google proxy) vs. Bing
   - Chose Tavily: better for AI, includes relevance scoring
2. **Content Extraction**: Firecrawl vs. BeautifulSoup vs. Trafilatura
   - Chose Firecrawl: handles JS rendering, cleaner output
3. **Summarization**: One summary vs. per-page summaries
   - Chose per-page: better attribution, more flexible

## Out of Scope

- Caching search results across sessions
- Custom search engine configuration
- Image/video search
- Real-time crawling of dynamic sites

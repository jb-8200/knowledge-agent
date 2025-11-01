# Step 02: Wrap Retrieval Logic as LangChain Tool

## Objective

Expose the vector search functionality as a composable LangChain Tool that can be used within chains, agents, and LangGraph workflows. The tool should have a clear interface, type validation, and JSON-serializable output.

## Atomic Implementation

This step is atomic: it either creates a working LangChain tool wrapper with proper schema and integration, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected tool behavior:

```python
# tests/test_retriever_tool.py
import pytest
from app.tools.retriever import retrieval_tool, retrieve_passages, RetrievalInput
from langchain.tools import BaseTool
from pydantic import ValidationError

def test_retrieval_tool_is_structured_tool():
    """Test that retrieval_tool is a LangChain tool."""
    assert isinstance(retrieval_tool, BaseTool)
    assert retrieval_tool.name == "search_knowledge_base"
    assert len(retrieval_tool.description) > 0

def test_retrieval_tool_has_input_schema():
    """Test that tool has Pydantic input schema."""
    assert retrieval_tool.args_schema is not None
    assert retrieval_tool.args_schema == RetrievalInput

def test_retrieval_input_schema_validation():
    """Test that RetrievalInput validates input correctly."""
    # Valid input
    valid_input = RetrievalInput(query="test query", top_k=5)
    assert valid_input.query == "test query"
    assert valid_input.top_k == 5

    # Default top_k
    default_input = RetrievalInput(query="another query")
    assert default_input.top_k == 5

    # Invalid: empty query
    with pytest.raises(ValidationError):
        RetrievalInput(query="", top_k=5)

    # Invalid: top_k out of range
    with pytest.raises(ValidationError):
        RetrievalInput(query="test", top_k=0)

def test_retrieve_passages_function_signature():
    """Test that retrieve_passages has correct signature."""
    import inspect
    sig = inspect.signature(retrieve_passages)

    assert 'query' in sig.parameters
    assert 'top_k' in sig.parameters
    assert sig.parameters['top_k'].default == 5

def test_retrieve_passages_returns_dict(monkeypatch):
    """Test that retrieve_passages returns JSON-serializable dict."""
    # Mock VectorSearchService
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Machine learning is a field of AI.",
            metadata={
                "doc_id": "doc1",
                "filename": "test.pdf",
                "chunk_index": 0,
                "page_number": 1,
                "source": "upload",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            score=0.95
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieve_passages(query="AI", top_k=3)

    assert isinstance(result, dict)
    assert "passages" in result
    assert "query" in result
    assert "count" in result
    assert result["query"] == "AI"
    assert result["count"] == 1
    assert len(result["passages"]) == 1

def test_retrieve_passages_output_format(monkeypatch):
    """Test that passages have correct structure."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Test passage",
            metadata={
                "doc_id": "doc1",
                "filename": "test.pdf",
                "chunk_index": 0,
                "source": "upload"
            },
            score=0.85
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieve_passages("test", top_k=1)
    passage = result["passages"][0]

    assert "text" in passage
    assert "metadata" in passage
    assert "score" in passage
    assert passage["text"] == "Test passage"
    assert passage["score"] == 0.85

def test_retrieval_tool_direct_invocation(monkeypatch):
    """Test invoking tool directly with tool.func()."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="LangChain is a framework.",
            metadata={"doc_id": "doc2", "filename": "docs.pdf", "chunk_index": 5, "source": "web"},
            score=0.92
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Invoke tool
    result = retrieval_tool.func(query="LangChain", top_k=1)

    assert result["count"] == 1
    assert result["passages"][0]["text"] == "LangChain is a framework."

def test_retrieval_tool_invoke_method(monkeypatch):
    """Test invoking tool with .invoke() method."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Testing invoke method.",
            metadata={"doc_id": "doc3", "filename": "test.md", "chunk_index": 0, "source": "upload"},
            score=0.88
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Use invoke method
    result = retrieval_tool.invoke({"query": "test invoke", "top_k": 1})

    assert isinstance(result, dict)
    assert result["count"] == 1

def test_retrieval_tool_with_langchain_chain(monkeypatch):
    """Test that tool works in a simple LangChain chain."""
    from app.services.vector_search import SearchResult
    from langchain.schema import AgentAction

    mock_results = [
        SearchResult(
            text="Chain integration test.",
            metadata={"doc_id": "doc4", "filename": "chain.pdf", "chunk_index": 2, "source": "upload"},
            score=0.90
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Test tool in chain-like context
    tool_input = {"query": "chain test", "top_k": 1}
    result = retrieval_tool.invoke(tool_input)

    assert result is not None
    assert "passages" in result

def test_empty_query_error_handling():
    """Test that empty queries are handled gracefully."""
    with pytest.raises(ValidationError, match="query"):
        RetrievalInput(query="", top_k=5)

def test_retrieve_passages_handles_no_results(monkeypatch):
    """Test that function handles empty search results."""
    def mock_search(self, query, top_k):
        return []

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieve_passages("nonexistent query", top_k=5)

    assert result["count"] == 0
    assert result["passages"] == []
    assert result["query"] == "nonexistent query"

def test_tool_output_is_json_serializable(monkeypatch):
    """Test that tool output can be serialized to JSON."""
    import json
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="JSON serialization test.",
            metadata={"doc_id": "doc5", "filename": "test.pdf", "chunk_index": 1, "source": "upload"},
            score=0.87
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieval_tool.invoke({"query": "JSON test", "top_k": 1})

    # Should not raise exception
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Parse back
    parsed = json.loads(json_str)
    assert parsed["count"] == 1
```

**Expected Result**: All tests fail because retriever tool doesn't exist yet.

### Green Phase

1. **Create retrieval tool implementation**:

```python
# app/tools/retriever.py
"""LangChain tool for retrieving passages from knowledge base."""

from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from app.services.vector_search import VectorSearchService
import logging

logger = logging.getLogger(__name__)

class RetrievalInput(BaseModel):
    """Input schema for retrieval tool."""
    query: str = Field(
        ...,
        description="The question or search query to find relevant passages for",
        min_length=1,
        max_length=1000
    )
    top_k: int = Field(
        default=5,
        description="Number of most relevant passages to retrieve (1-20)",
        ge=1,
        le=20
    )

def retrieve_passages(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Retrieve top-k passages relevant to the query from knowledge base.

    This function searches the vector database for passages most similar
    to the input query and returns them with metadata and scores.

    Args:
        query: The search query or question
        top_k: Number of passages to retrieve (default: 5, max: 20)

    Returns:
        Dictionary containing:
        - passages: List of passage dicts with text, metadata, and scores
        - query: The original query string
        - count: Number of results returned

    Example:
        >>> result = retrieve_passages("What is machine learning?", top_k=3)
        >>> print(f"Found {result['count']} passages")
        >>> for passage in result['passages']:
        ...     print(passage['text'][:100])
    """
    logger.info(f"Retrieving passages for query: '{query[:50]}...' (top_k={top_k})")

    try:
        # Initialize search service
        search_service = VectorSearchService()

        # Search for relevant passages
        results = search_service.search_vectors(query=query, top_k=top_k)

        # Convert to JSON-serializable format
        passages = []
        for result in results:
            passages.append({
                "text": result.text,
                "metadata": result.metadata,
                "score": result.score
            })

        logger.info(f"Retrieved {len(passages)} passages")

        return {
            "passages": passages,
            "query": query,
            "count": len(passages)
        }

    except Exception as e:
        logger.error(f"Retrieval failed: {str(e)}")
        # Return empty result instead of crashing
        return {
            "passages": [],
            "query": query,
            "count": 0,
            "error": str(e)
        }

# Create LangChain StructuredTool
retrieval_tool = StructuredTool(
    name="search_knowledge_base",
    description=(
        "Search the internal knowledge base for passages relevant to a query. "
        "Returns text snippets from documents with metadata (filename, page number, source) "
        "and similarity scores. Use this when you need to find information from "
        "previously uploaded documents or web pages."
    ),
    func=retrieve_passages,
    args_schema=RetrievalInput,
    return_direct=False  # Allow chain to process results
)
```

2. **Create tools package init**:

```python
# app/tools/__init__.py
from .retriever import retrieval_tool, retrieve_passages, RetrievalInput

__all__ = ["retrieval_tool", "retrieve_passages", "RetrievalInput"]
```

3. **Run tests**:

```bash
pytest tests/test_retriever_tool.py -v
```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add retry logic** for transient failures:

```python
# app/tools/retriever.py
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from qdrant_client.http.exceptions import UnexpectedResponse

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(UnexpectedResponse),
    reraise=True
)
def retrieve_passages(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Retrieve top-k passages with retry logic for transient failures."""
    logger.info(f"Retrieving passages for query: '{query[:50]}...' (top_k={top_k})")

    # ... rest of implementation
```

2. **Add result caching** for repeated queries:

```python
# app/tools/retriever.py
from functools import lru_cache
import hashlib

def cache_key(query: str, top_k: int) -> str:
    """Generate cache key for query."""
    content = f"{query}:{top_k}"
    return hashlib.md5(content.encode()).hexdigest()

# Simple in-memory cache (for development)
# In production, use Redis or similar
_result_cache: Dict[str, Dict[str, Any]] = {}
CACHE_SIZE = 100

def retrieve_passages(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Retrieve passages with caching."""
    # Check cache
    key = cache_key(query, top_k)
    if key in _result_cache:
        logger.info(f"Cache hit for query: '{query[:50]}...'")
        return _result_cache[key]

    logger.info(f"Retrieving passages for query: '{query[:50]}...' (top_k={top_k})")

    try:
        # ... search logic ...

        result = {
            "passages": passages,
            "query": query,
            "count": len(passages)
        }

        # Cache result
        if len(_result_cache) >= CACHE_SIZE:
            # Simple eviction: remove oldest entry
            _result_cache.pop(next(iter(_result_cache)))
        _result_cache[key] = result

        return result

    except Exception as e:
        # ... error handling ...
```

3. **Add detailed logging** with metrics:

```python
# app/tools/retriever.py
import time

def retrieve_passages(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Retrieve passages with detailed logging."""
    start_time = time.time()

    logger.info(
        f"Retrieval request: query_len={len(query)}, top_k={top_k}, "
        f"query_preview='{query[:50]}...'"
    )

    try:
        # ... search logic ...

        elapsed = (time.time() - start_time) * 1000  # ms
        logger.info(
            f"Retrieval completed: count={len(passages)}, "
            f"elapsed={elapsed:.1f}ms, "
            f"top_score={passages[0]['score'] if passages else 'N/A'}"
        )

        return result

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(
            f"Retrieval failed: error={str(e)}, "
            f"elapsed={elapsed:.1f}ms"
        )
        # ... return empty result ...
```

4. **Create example chain integration**:

```python
# tests/test_retriever_tool.py (add integration test)
def test_tool_in_langchain_chain_example(monkeypatch):
    """Example of using retrieval tool in a LangChain chain."""
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage
    from app.services.vector_search import SearchResult

    # Mock search results
    mock_results = [
        SearchResult(
            text="LangChain enables building LLM applications.",
            metadata={"doc_id": "doc1", "filename": "langchain.pdf", "chunk_index": 0, "source": "upload"},
            score=0.95
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Example: Retrieve then format for LLM
    retrieval_result = retrieval_tool.invoke({"query": "What is LangChain?", "top_k": 3})

    # Format passages for LLM context
    context = "\n\n".join([
        f"[Source: {p['metadata']['filename']}]\n{p['text']}"
        for p in retrieval_result["passages"]
    ])

    assert len(context) > 0
    assert "LangChain enables" in context
```

5. **Add tool usage documentation**:

```python
# app/tools/retriever.py (add docstring examples)
"""
Usage Examples
--------------

Direct invocation:
    >>> from app.tools.retriever import retrieval_tool
    >>> result = retrieval_tool.invoke({"query": "machine learning", "top_k": 3})
    >>> print(result["count"])
    3

In LangChain chain:
    >>> from langchain.agents import initialize_agent, AgentType
    >>> from langchain.llms import OpenAI
    >>> tools = [retrieval_tool]
    >>> agent = initialize_agent(tools, OpenAI(), agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
    >>> agent.run("What do my documents say about AI?")

In LangGraph:
    >>> from langgraph.prebuilt import ToolNode
    >>> tool_node = ToolNode([retrieval_tool])
    >>> # Add to graph workflow
"""
```

6. **Commit changes**:

```bash
git add .
git commit -m "feat: wrap vector search as LangChain tool

- Create retrieval_tool using LangChain StructuredTool
- Define RetrievalInput schema with Pydantic validation
- Implement retrieve_passages function with JSON-serializable output
- Add retry logic for transient Qdrant failures
- Add result caching for repeated queries (in-memory)
- Add comprehensive logging with timing metrics
- Tests verify tool invocation, schema validation, chain integration
- Examples demonstrate usage in chains and agents

Covers Task 09 from original requirements.
All tests passing.
"
```

## Acceptance Criteria Verification

- [x] retrieval_tool is a LangChain StructuredTool instance
- [x] Tool has descriptive name ("search_knowledge_base")
- [x] Tool has clear description for LLM understanding
- [x] RetrievalInput schema validates query and top_k parameters
- [x] Empty queries rejected by Pydantic validation
- [x] retrieve_passages returns JSON-serializable dict
- [x] Output includes passages, query, and count fields
- [x] Passages include text, metadata, and score
- [x] Tool invocable via .func() and .invoke() methods
- [x] Tool works in LangChain chain context
- [x] Empty search results handled gracefully
- [x] All tests pass

## Files Created/Modified

- Created: `app/tools/retriever.py`
- Created: `app/tools/__init__.py`
- Created: `tests/test_retriever_tool.py`

## Rollback Strategy

If this step fails:
1. Remove `app/tools/retriever.py`
2. Remove `tests/test_retriever_tool.py`
3. Run `git reset --hard HEAD~1`
4. Review errors (check LangChain version compatibility)
5. Retry step from Red phase

## Dependencies

Requires:
- Step 01 completed (VectorSearchService available)
- LangChain installed: `pip install langchain`
- Pydantic for schema validation (included with LangChain)
- tenacity for retry logic: `pip install tenacity`

## Testing the Tool Manually

Test in Python REPL:

```python
from app.tools.retriever import retrieval_tool, retrieve_passages

# Direct function call
result = retrieve_passages("What is artificial intelligence?", top_k=3)
print(f"Found {result['count']} passages")
for i, passage in enumerate(result['passages'], 1):
    print(f"\n{i}. Score: {passage['score']:.3f}")
    print(f"   {passage['text'][:100]}...")

# Tool invocation (LangChain style)
result = retrieval_tool.invoke({
    "query": "machine learning algorithms",
    "top_k": 5
})
print(result)

# Check tool metadata
print(f"Tool name: {retrieval_tool.name}")
print(f"Description: {retrieval_tool.description}")
print(f"Input schema: {retrieval_tool.args_schema.schema()}")
```

Test in LangChain chain:

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI  # or any LLM
from app.tools.retriever import retrieval_tool

# Create agent with retrieval tool
agent = initialize_agent(
    tools=[retrieval_tool],
    llm=OpenAI(temperature=0),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Ask question that requires retrieval
response = agent.run("What information do you have about neural networks?")
print(response)
```

## Next Step

Proceed to `03_session_memory.md` - Implement session and memory services

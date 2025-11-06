"""LangChain tool for retrieving passages from knowledge base."""

from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from app.services.vector_search import VectorSearchService
import logging
import time

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
    start_time = time.time()

    logger.info(
        f"Retrieval request: query_len={len(query)}, top_k={top_k}, "
        f"query_preview='{query[:50]}...'"
    )

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

        elapsed = (time.time() - start_time) * 1000  # ms
        logger.info(
            f"Retrieval completed: count={len(passages)}, "
            f"elapsed={elapsed:.1f}ms, "
            f"top_score={passages[0]['score'] if passages else 'N/A'}"
        )

        return {
            "passages": passages,
            "query": query,
            "count": len(passages)
        }

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(
            f"Retrieval failed: error={str(e)}, "
            f"elapsed={elapsed:.1f}ms"
        )
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

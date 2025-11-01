# Spec 09 – Wrap the retrieval logic as a LangChain tool

LangChain provides the `Tool` and `StructuredTool` classes to expose deterministic functions to LLM chains or agents.  This specification shows how to wrap the vector search function from Spec 08.

## Function Definition

Define the retrieval function:

```python
def retrieve_passages(query: str, top_k: int = 5) -> dict:
    """Return top‑k passages relevant to the query with metadata and scores."""
    passages = search_vectors(query, top_k)
    return {"passages": passages}
```

## Register as a LangChain Tool

Wrap the function using the `Tool` class:

```python
from langchain.tools import Tool

retrieval_tool = Tool(
    name="internal_retrieval",
    description="Retrieve top‑k internal document passages for a given query",
    func=lambda query: retrieve_passages(query=query, top_k=5),
)
```

Alternatively, if you need structured input validation and type hints, use `StructuredTool`:

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel

class RetrievalInput(BaseModel):
    query: str
    top_k: int = 5

retrieval_tool = StructuredTool(
    name="internal_retrieval",
    description="Retrieve top‑k internal document passages for a given query",
    func=lambda query, top_k=5: retrieve_passages(query, top_k),
    args_schema=RetrievalInput,
    return_direct=True,
)
```

Add this `retrieval_tool` to the list of tools used by your chains or agent.  During execution, the LLM can call it to obtain relevant passages.

## Tool Output Format

Ensure that the function returns JSON‑serializable objects (dicts, lists) and includes enough metadata (document identifiers, chunk indices, scores) for later citation.  The LangChain tool can return complex data, but keep the schema as simple as possible for the downstream chains.

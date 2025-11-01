# Task 09 – Wrap the retrieval logic as a LangChain tool

**Phase:** Internal Retrieval (RAG)

**Description:**

Expose the vector search functionality (Task 08) as a callable tool within LangChain.  Define a Python function with a clear signature (e.g., `def retrieve_passages(query: str, top_k: int = 5) -> dict`) that returns the top‑K passages and metadata.  Use `langchain.tools` or `langchain.utilities` to wrap this function as a `Tool` or `StructuredTool`, providing a name and description.  Register the tool so that it can be used within LangChain chains or graphs.

**Acceptance Criteria:**

* The retrieval function is defined and returns JSON‑serializable data.
* The function is wrapped using a LangChain `Tool` or `StructuredTool` with a descriptive name.
* Example code demonstrates how to invoke the tool directly and via a chain.
* Unit tests confirm that the tool returns expected passages when given a sample query.

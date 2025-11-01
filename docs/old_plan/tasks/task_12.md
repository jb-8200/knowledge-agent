# Task 12 – Wrap the external search tool as a LangChain tool

**Phase:** External Search Integration

**Description:**

Instantiate a web search client and wrap it as a LangChain tool.  For example, use `langchain.utilities.tavily_search.TavilySearchResults` or `langchain.utilities.serper.SerperSearchResults` depending on the chosen provider.  Define a function that accepts a query and returns a list of search result objects (URL, title, snippet).  Wrap this function using `Tool` or `StructuredTool` with an appropriate name and description.  Ensure that the tool can be called within LangChain chains or graphs.

**Acceptance Criteria:**

* The search client is properly configured with the API key from the environment.
* A function exists that returns search results in a structured format (list of dicts).
* The function is wrapped as a LangChain tool and can be invoked programmatically.
* Unit tests mock the search API and verify that the tool returns expected results and handles errors (e.g., API quota exceeded).

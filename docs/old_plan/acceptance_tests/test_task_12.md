# Acceptance Test for Task 12 – Wrap the external search tool as a LangChain tool

**Objective:** Ensure that the external search provider is integrated into the agent workflow using a LangChain tool.

**Test Steps:**

1. Instantiate a search client (e.g., `TavilySearchResults` or `SerperSearchWrapper`) using the API key provided in the environment.
2. Wrap the search function using LangChain’s `Tool` or `StructuredTool`, giving it a descriptive name (e.g., `web_search`) and description.
3. Integrate the search tool into a LangChain chain or agent that can be triggered when the internal retrieval signals missing information.
4. Execute a query that should trigger external search and verify that the wrapped search tool is called and returns search results.
5. Verify that the returned search results include URLs, titles and snippet text, and that they are available for summarization by downstream components.

**Expected Result:** The external search tool is properly wrapped and callable via the agent; search results are returned in a structured format.

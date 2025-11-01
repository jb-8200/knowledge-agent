# Spec 12 – Wrap the external search tool as a LangChain tool

To integrate external search into the agent workflow, you need to instantiate a search client and wrap it as a LangChain tool.

## Tavily Example

Assuming you choose Tavily as your search provider, use the `langchain.utilities.tavily_search.TavilySearchResults` utility:

```python
from langchain.utilities import TavilySearchResults
from langchain.tools import Tool
import os

search = TavilySearchResults(k=5, api_key=os.environ["SEARCH_API_KEY"])

def perform_web_search(query: str, k: int = 5) -> list[dict]:
    """Return a list of search results with `title`, `url` and `content`."""
    results = search.results(query)
    # Map Tavily’s result format to a standard dict
    return [
        {"title": r["title"], "url": r["url"], "snippet": r.get("content", "")}
        for r in results
    ]

search_tool = Tool(
    name="web_search",
    description="Perform a web search and return a list of URLs and snippets",
    func=lambda query: perform_web_search(query=query, k=5),
)
```

## Serper Example

For Serper, the integration is similar:

```python
from langchain.utilities import SerperSearchWrapper

search = SerperSearchWrapper(api_key=os.environ["SEARCH_API_KEY"])

def perform_web_search(query: str, k: int = 5):
    response = search.run(query)
    # Parse response into a list of dicts (title, url, snippet)
    ...
```

## Tool Registration

Wrap the search function using `Tool` or `StructuredTool` as shown above.  Provide a clear description so the model knows when to call the tool.  Add the tool to your list of tools used by the workflow.  If you expect to switch providers, write a factory function that returns the appropriate tool based on configuration.

## Error Handling

Catch exceptions from the search client (network errors, quota exceeded) and return a controlled error message or an empty list.  Downstream components should handle an empty result gracefully by skipping external summarization.

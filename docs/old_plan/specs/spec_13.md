# Spec 13 – Summarize external snippets

External search results often contain multiple snippets that must be condensed for efficient reasoning.  This specification outlines the summarization process.

## Summary Extraction

1. **Fetch Page Content:** For each URL returned by the search tool, invoke Firecrawl to fetch and extract the main content of the page.  Use asynchronous HTTP requests to improve throughput.
2. **Initial Cleanup:** Remove boilerplate text (headers, footers, navigation menus) if Firecrawl does not do so automatically.
3. **Chunking:** If the page is long, split it into smaller sections (e.g., paragraphs) before summarization.
4. **LLM Summarization:** Use a LangChain `LLMChain` with a prompt instructing the model to produce a concise summary of the extracted content and include a citation (the URL or an ID).  Summarize each page separately.
5. **Aggregation:** Combine individual summaries into a single external summary that lists key facts and citations.

## Example Implementation

```python
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

# Define a prompt template
summary_prompt = PromptTemplate(
    input_variables=["page_text", "source"],
    template=(
        "You are summarizing a web page for a knowledge base."
        " Given the following page text, write a concise factual summary."
        " Include the citation in brackets, e.g., [{{ source }}].\n\n"
        "Page Text:\n{{ page_text }}"
    ),
)

llm = OpenAI(api_key=os.environ.get("MODEL_PROVIDER_API_KEY"), temperature=0)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

async def summarize_page(page_text: str, url: str) -> str:
    return summary_chain.run(page_text=page_text, source=url)

async def summarize_search_results(results: list[dict]) -> list[dict]:
    summaries = []
    for res in results:
        content = await fetch_page_content(res["url"])  # Firecrawl call
        summary = await summarize_page(content, res["url"])
        summaries.append({"summary": summary, "citation": res["url"]})
    return summaries
```

## Error Handling

* **Fetch errors:** If Firecrawl fails to retrieve a page, skip that result and optionally log it.
* **Content length:** For very long pages, truncate or split into segments before summarization to avoid exceeding model token limits.
* **Deduplication:** Remove duplicate summaries if multiple search results point to the same domain or content.

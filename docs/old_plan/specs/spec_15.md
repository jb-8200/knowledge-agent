# Spec 15 – Define the external summarizer chain

After obtaining summaries of individual web pages (Spec 13), the external summarizer chain combines them into a unified external narrative.

## Prompt Template

```python
from langchain.prompts import PromptTemplate

external_prompt = PromptTemplate(
    input_variables=["summaries"],
    template=(
        "You are aggregating information from external sources."
        " Combine the following summaries into a coherent set of factual statements."
        " For each fact, include the citation number corresponding to the source summary in brackets."
        " Do not introduce any information not present in the summaries.\n\n"
        "Summaries:\n{{ summaries }}\n\n"
        "Combined Summary:"
    ),
)
```

## Chain Definition

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(api_key=os.environ.get("MODEL_PROVIDER_API_KEY"), temperature=0)
external_chain = LLMChain(llm=llm, prompt=external_prompt)

def run_external_summarizer(summaries: list[dict]) -> dict:
    # Format summaries with indices for citations
    formatted = "\n".join([
        f"[{i+1}] {s['summary']}" for i, s in enumerate(summaries)
    ])
    combined = external_chain.run(summaries=formatted)
    citations = [s["citation"] for s in summaries]
    return {"summary": combined, "citations": citations}
```

## Notes

* Keep the temperature low to encourage factual consolidation.
* Ensure that the input order corresponds to the citation order in the output.
* If the combined summary becomes too long, consider truncating or splitting it into paragraphs.

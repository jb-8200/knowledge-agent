# Spec 22 – Generate similar questions

After answering a query, the system should suggest related questions that users might ask.  This specification describes how to implement this functionality.

## LLM Prompt

Define a prompt instructing the model to produce follow‑up questions:

```python
from langchain.prompts import PromptTemplate

similar_prompt = PromptTemplate(
    input_variables=["question"],
    template=(
        "Given the question below, generate up to five related questions that a curious person might ask next."
        " Avoid repeating the original question and keep each suggestion concise."
        "\n\n"
        "Original Question: {{ question }}\n\n"
        "Suggested Questions:"
    ),
)
```

## Chain Implementation

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(api_key=os.environ.get("MODEL_PROVIDER_API_KEY"), temperature=0.7)
similar_chain = LLMChain(llm=llm, prompt=similar_prompt)

def generate_related_questions(question: str) -> list[str]:
    response = similar_chain.run(question=question)
    # Split the response into separate questions by newline or number markers
    suggestions = [q.strip("• ") for q in response.strip().split("\n") if q.strip()]
    return suggestions[:5]
```

## Considerations

* Use a slightly higher temperature to encourage diversity in suggestions.
* Post‑process the output to remove duplicates and empty strings.
* If no related questions are generated, return an empty list.

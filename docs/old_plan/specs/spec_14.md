# Spec 14 – Define the synthesizer chain

The synthesizer chain drafts an answer using only passages from the internal corpus.  It must cite its sources and indicate whether external information is needed.

## Prompt Template

Define a prompt that instructs the LLM to use only the provided passages to answer the user’s question:

```python
from langchain.prompts import PromptTemplate

synth_prompt = PromptTemplate(
    input_variables=["question", "passages"],
    template=(
        "You are a helpful assistant answering questions using provided passages."
        " Answer the question based only on these passages."
        " Cite each passage you use with a bracketed number in the order of appearance (e.g., [1], [2])."
        " If the information is insufficient, reply 'MORE_INFO_NEEDED' at the end.\n\n"
        "Question: {{ question }}\n\n"
        "Passages:\n{{ passages }}\n\n"
        "Answer:"
    ),
)
```

## Chain Definition

Instantiate an `LLMChain` using the prompt and a deterministic model:

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(api_key=os.environ.get("MODEL_PROVIDER_API_KEY"), temperature=0)
synth_chain = LLMChain(llm=llm, prompt=synth_prompt)

def run_synthesizer(question: str, passages: list[dict]) -> dict:
    # Format passages as a numbered list for the prompt
    formatted_passages = "\n".join(
        [f"[{i+1}] {p['text']}" for i, p in enumerate(passages)]
    )
    answer = synth_chain.run(question=question, passages=formatted_passages)
    needs_external = answer.strip().endswith("MORE_INFO_NEEDED")
    # Remove the flag from the answer text
    if needs_external:
        answer = answer.replace("MORE_INFO_NEEDED", "").strip()
    return {"answer": answer, "needs_external": needs_external, "citations": [p["metadata"] for p in passages]}
```

## Considerations

* Use a deterministic model or a low temperature to minimize hallucinations.
* The `needs_external` flag is indicated by a magic string; you can also ask the model to output a JSON object instead.
* If your model provider supports function calling or JSON mode, consider using it for more structured outputs.

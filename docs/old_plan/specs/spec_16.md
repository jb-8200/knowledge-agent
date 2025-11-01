# Spec 16 – Define the critic chain

The critic chain produces the final answer by combining internal and external summaries, resolving contradictions and ordering citations.

## Prompt Template

```python
from langchain.prompts import PromptTemplate

critic_prompt = PromptTemplate(
    input_variables=["question", "internal_answer", "external_summary"],
    template=(
        "You are a critical reviewer combining two sources of information."
        " Given the question, an internal answer based on uploaded documents and an external summary from the web,"
        " craft a final answer that integrates both.  Resolve any contradictions by preferring internal content unless the external source clearly corrects it."
        " Provide citations for each statement, numbering internal citations first (e.g., [1], [2]) and then external citations (e.g., [E1], [E2])."
        " If any information is uncertain or conflicted, mention it explicitly.\n\n"
        "Question: {{ question }}\n\n"
        "Internal Answer:\n{{ internal_answer }}\n\n"
        "External Summary:\n{{ external_summary }}\n\n"
        "Final Answer:"
    ),
)
```

## Chain Definition

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(api_key=os.environ.get("MODEL_PROVIDER_API_KEY"), temperature=0)
critic_chain = LLMChain(llm=llm, prompt=critic_prompt)

def run_critic(question: str, internal: dict, external: dict) -> dict:
    final_answer = critic_chain.run(
        question=question,
        internal_answer=internal["answer"],
        external_summary=external["summary"]
    )
    # Combine citations: internal citations first, then external
    citations = internal["citations"] + external["citations"]
    return {"answer": final_answer.strip(), "citations": citations}
```

## Considerations

* Clarify in the prompt that internal information has higher priority when conflicts arise.
* Use distinct citation prefixes (e.g., E1, E2) for external sources to avoid confusion.
* Post‑process the final answer to ensure citations appear in the order they are defined.

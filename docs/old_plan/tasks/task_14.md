# Task 14 – Define the synthesizer chain

**Phase:** CAG Modules & Orchestration

**Description:**

Create a LangChain `LLMChain` responsible for drafting an answer using only passages returned from the internal retrieval tool.  Construct a prompt template instructing the model to answer the user’s question based solely on the provided passages and to cite each passage (e.g., with bracketed numbers).  The chain should return both the draft answer and a flag (`needs_external`) indicating whether the model believes additional information is required.  Do not include external search logic in this chain.

**Acceptance Criteria:**

* An LLM chain is defined with a prompt template and an LLM instance.
* The chain accepts a query and a list of passages and returns a draft answer plus a `needs_external` flag.
* The answer includes citations corresponding to the passages used.
* Unit tests feed sample passages into the chain and assert that the output adheres to instructions and signals when external information is needed.

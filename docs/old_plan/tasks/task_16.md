# Task 16 – Define the critic chain

**Phase:** CAG Modules & Orchestration

**Description:**

Design a LangChain `LLMChain` to act as a critic that combines the internal draft answer and the external summary.  This chain should resolve contradictions, verify factual consistency, and produce a final answer with ordered citations (internal passages first, external sources second).  The prompt template should instruct the model to apply critical reasoning, remove redundancy and mark uncertain statements.  The chain returns the final answer and a list of citations in the order they appear.

**Acceptance Criteria:**

* A critic chain exists with a prompt that guides the model to merge internal and external content.
* The final answer includes all relevant citations, grouped or numbered according to their origin.
* Contradictory or unsupported statements are flagged or omitted.
* Unit tests check that the critic produces coherent answers when given conflicting inputs and properly orders citations.

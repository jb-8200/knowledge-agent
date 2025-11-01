# Acceptance Test for Task 14 – Define the CAG synthesizer agent

**Objective:** Ensure that the internal synthesizer agent produces a draft answer from retrieved passages and signals whether more information is needed.

**Test Steps:**

1. Feed the synthesizer agent with a set of passages retrieved from the vector store.
2. Verify that the agent outputs an answer that meaningfully combines information from the passages, cites them (e.g., [1], [2]) and is coherent.
3. Include test cases where the passages do not fully answer the query; the synthesizer should explicitly indicate that external information is needed (e.g., by returning a flag or a statement).
4. Confirm that the agent does not fabricate information beyond what is provided in the passages.
5. Test the agent on multiple topics to ensure consistent performance.

**Expected Result:** The synthesizer agent generates a draft answer grounded in internal passages, includes citations and correctly signals when external search should be triggered.

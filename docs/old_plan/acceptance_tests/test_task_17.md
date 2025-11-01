# Acceptance Test for Task 17 – Compose the Sequential workflow agent

**Objective:** Ensure that the workflow agent orchestrates retrieval, synthesis, external search, external synthesis and criticism in the correct sequence.

**Test Steps:**

1. Instantiate the workflow agent with the retrieval tool, synthesizer agent, external search tool, external synthesizer and critic.
2. Ask a question that can be answered from internal documents; observe that the agent retrieves passages, synthesizes an answer and returns a final response without calling external search.
3. Ask a question that cannot be fully answered internally; observe that after the synthesizer signals missing information, the workflow calls the external search tool and external synthesizer before invoking the critic.
4. Inspect the agent’s internal logs or traces to verify the order of operations.
5. Confirm that the final response includes citations from both internal and external sources when external search is used.

**Expected Result:** The workflow agent correctly sequences each step based on the synthesizer’s signal, producing accurate answers with appropriate citations.

# Acceptance Test for Task 16 – Define the CAG critic agent

**Objective:** Verify that the critic agent merges internal and external summaries, resolves contradictions and produces a final answer with ordered citations.

**Test Steps:**

1. Supply the critic agent with an internal summary and an external summary, both containing citations and potentially overlapping information.
2. Observe the agent’s output; it should combine relevant facts, eliminate duplicates and highlight any contradictions (resolving them or flagging uncertainty).
3. Ensure that citations are reordered and deduplicated in the final answer.
4. Test scenarios where internal and external information conflict; the critic should favor internal sources for truth while incorporating credible external details.
5. Confirm that the final answer is coherent, respects length constraints and adheres to the specified answer format.

**Expected Result:** The critic agent outputs a final answer that synthesizes internal and external content, resolves conflicts, orders citations and clearly references sources.

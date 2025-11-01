# Acceptance Test for Task 15 – Define the external synthesizer agent

**Objective:** Confirm that the external synthesizer summarizes external search results into structured information with citations.

**Test Steps:**

1. Provide the external synthesizer agent with a collection of search result snippets and metadata.
2. Run the agent and inspect the output; it should produce a summarized answer that references external sources and clearly delineates them from internal sources.
3. Validate that the agent extracts factual statements without hallucinations and preserves key details such as names, dates or figures.
4. Check that citations correspond to the specific search results used in the summary.
5. Test with varied and potentially conflicting snippets to ensure the agent balances information appropriately.

**Expected Result:** The external synthesizer creates a coherent summary of external information, includes citations and is ready for integration by the critic.

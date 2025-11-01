# Acceptance Test for Task 13 – Summarize external snippets

**Objective:** Validate that the system condenses external search results into concise passages.

**Test Steps:**

1. Provide a set of external search results (via the search tool or a mock) containing multiple snippets.
2. Invoke the summarization logic responsible for condensing these snippets.
3. Check that the output summary captures the key facts from the snippets, omits irrelevant information and includes references (e.g., indices or URLs) to the original results.
4. Ensure that the summarizer respects length constraints and produces a coherent paragraph or bullet list.
5. Test summarization when the number of snippets is large; the summarizer should select the most relevant ones.

**Expected Result:** External snippets are summarized into a concise form with preserved citations, ready to be combined with the internal answer.

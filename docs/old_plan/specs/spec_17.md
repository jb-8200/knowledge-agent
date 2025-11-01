# Spec 17 – Compose the workflow

This specification outlines how to orchestrate the retrieval, synthesis, external search and criticism steps.

## High‑Level Workflow

1. **Retrieve session context:** Determine the current session ID and load conversation history and pinned notes.
2. **Call internal retrieval:** Use the retrieval tool to obtain top‑K passages from Qdrant based on the user’s query.
3. **Run synthesizer:** Pass the query and retrieved passages to the synthesizer chain to generate a draft answer and a `needs_external` flag.
4. **Conditionally run external search:** If `needs_external` is true, call the external search tool and summarize the results using Firecrawl and the external summarizer chain.  Otherwise, skip this step.
5. **Run critic:** Combine the synthesizer output and external summary (if any) using the critic chain to produce the final answer and ordered citations.
6. **Update memory:** Save the question, answer, citations and any pinned notes in session memory.
7. **Return response:** Build a response payload containing the final answer, citation mapping (internal documents and external URLs), list of related documents, external links, YouTube thumbnails, similar questions and pinned notes.

## Implementation Sketch

```python
async def handle_query(question: str, session_id: str) -> dict:
    session = get_session(session_id)
    # Step 2: internal retrieval
    internal_passages = retrieval_tool.func(question)
    # Step 3: synthesizer
    synth_output = run_synthesizer(question, internal_passages["passages"])
    external_output = {"summary": "", "citations": []}
    # Step 4: external search if needed
    if synth_output["needs_external"]:
        search_results = search_tool.func(question)
        summaries = await summarize_search_results(search_results)
        external_output = run_external_summarizer(summaries)
    # Step 5: critic
    final_output = run_critic(question, synth_output, external_output)
    # Step 6: memory update
    record_interaction(session_id, question, final_output["answer"])
    # Build response
    response = {
        "answer": final_output["answer"],
        "citations": final_output["citations"],
        "internal_links": internal_passages["passages"],
        "external_links": external_output.get("citations", []),
        # Add YouTube thumbnails and similar questions via Tasks 21 & 22
        # Add pinned notes from session
    }
    return response
```

## LangGraph Option

For more complex workflows, consider using [LangGraph](https://python.langchain.com/docs/langgraph) to define a state machine with nodes representing each step and edges that depend on conditions (e.g., whether external search is needed).  This allows you to visualize and test the workflow more easily.

# Spec 36 – Create evaluation harness

This specification describes how to implement an evaluation harness for
the knowledge‑base agent.  The goal is to systematically test the
agent’s answers against representative questions to detect
regressions and measure improvements over time.  The harness draws
inspiration from RAG evaluation frameworks (e.g., RAGAS) and uses a
corpus of “golden queries” defined in YAML.

## Steps

1. **Define golden queries.**  Create a directory `evals/` at the
   project root (if it does not already exist) and add a file
   `golden-queries.yaml`.  Each entry in this file should have the
   following keys:

   - `query`: The user question.
   - `expected_points`: A list of key facts or concepts that
     correct answers should mention.
   - `allowed_sources`: A list of domain patterns or document IDs
     that are acceptable for citations.

   For example:

   ```yaml
   - query: "What is LangChain and how does it support RAG?"
     expected_points:
       - "LangChain is a framework for building applications with LLMs"
       - "It provides abstractions for chains, tools and agents"
       - "Supports vector stores like Qdrant"
     allowed_sources:
       - "langchain.com"
       - "docs/"
   - query: "How does Firecrawl differ from simple web scraping?"
     expected_points:
       - "Firecrawl fetches and parses full web pages"
       - "It provides structured outputs for LLM consumption"
       - "Avoids reliance on search snippets alone"
     allowed_sources:
       - "firecrawl.ai"
       - "docs/"
   ```

2. **Implement the evaluation script.**  Provide a script or a set of
   instructions (e.g., in the developer guide) that performs the
   following steps:

   - Load the `golden-queries.yaml` file.
   - For each query, call the agent via the API (or directly in
     memory) to obtain an answer and its citations.
   - Check whether each `expected_point` appears in the answer.  Use
     simple string matching or a more sophisticated semantic
     similarity metric as needed.
   - Verify that the cited sources match one of the patterns in
     `allowed_sources`.  Disallow citations from unknown domains.
   - Record metrics such as precision (fraction of expected points
     mentioned), recall, citation validity and answer length.
   - Produce a human‑readable report summarizing the metrics per
     query and overall statistics.

3. **Automate nightly evaluation.**  Integrate the script into your
   continuous integration pipeline or schedule it to run nightly.
   Store the evaluation results (e.g., in JSON or CSV) and surface
   them in a dashboard or metrics tool.  Use these results to
   identify regressions early and guide prompt or model
   improvements.

## Notes

* Golden queries should be updated regularly to reflect real user
  questions and edge cases discovered during deployment.  Keep the
  list concise (e.g., 10–50 queries) to make the nightly runs
  manageable.
* The evaluation harness is a lightweight alternative to agent
  training frameworks.  It does not modify the model weights but
  provides objective metrics for retrieval and reasoning quality.
* Consider using existing libraries such as RAGAS or LangChain’s
  evaluation utilities to simplify the implementation.
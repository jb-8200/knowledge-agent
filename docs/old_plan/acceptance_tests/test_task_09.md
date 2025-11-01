# Acceptance Test for Task 09 – Wrap the retrieval logic as a LangChain tool

**Objective:** Verify that the retrieval function is exposed as a tool callable within LangChain chains.

**Test Steps:**

1. Define the `retrieve_passages` function according to Spec 09 and wrap it using `Tool` or `StructuredTool`.
2. Invoke the tool directly with a sample query and confirm that it returns a dictionary containing a list of passages.
3. Build a simple `LLMChain` or scripted chain that calls the retrieval tool using LangChain’s tool invocation syntax.
4. Check that the tool execution is logged in the chain’s run history and that the returned passages are available for downstream processing.

**Expected Result:**

* The retrieval tool is callable via `tool.func` and returns the correct data structure.
* When used within a chain, the tool executes and passes results to subsequent steps.
* Tests confirm that the tool’s name and description are correctly defined and that no exceptions are raised.

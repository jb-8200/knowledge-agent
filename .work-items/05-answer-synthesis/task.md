# Task Breakdown: Answer Synthesis

## Overview

Implement a multi-stage answer generation system that synthesizes responses from internal knowledge base passages (RAG) and external web sources (CAG), with proper citation management and intelligent orchestration to determine when external information is needed.

## Requirements Traceability

- Links to: `user-story.md` - Research Analyst needs comprehensive, cited answers
- Links to: `design.md` - Multi-stage chain architecture and workflow design
- Original tasks: Task 14 (Synthesizer), Task 15 (External Summarizer), Task 16 (Critic), Task 17 (Workflow)

## Test Strategy

### Testing LLM Chains

LLM chains require specialized testing approaches due to non-deterministic behavior:

**Unit Tests**:
- Mock LLM responses to test parsing and control flow
- Test prompt template rendering with various inputs
- Validate citation extraction and formatting
- Test `needs_external` flag detection logic
- Verify error handling for API failures

**Integration Tests**:
- Use deterministic LLM (temperature=0) for repeatable outputs
- Test with fixed example passages and known good answers
- Verify citation ordering and format consistency
- Test conditional external search triggering
- Validate end-to-end workflow with mocked external services

**LLM Evaluation Tests**:
- Define golden datasets with question/passage/expected_answer triples
- Use assertion libraries (e.g., `langchain.evaluation`) for semantic similarity
- Test with multiple LLM calls and average results for flakiness
- Validate citations match actual source passages
- Check for hallucinations (claims not in sources)

**Acceptance Tests**:
- Test with real LLM API and actual retrieved passages
- Verify answers are coherent and well-cited
- Validate internal vs external citation distinction
- Test conflict resolution between sources
- Measure response quality with human evaluation

### Test Fixtures

Create reusable test data:
```python
# tests/fixtures/qa_fixtures.py
SAMPLE_PASSAGES = [
    {"text": "Python was created by Guido van Rossum...", "metadata": {...}},
    {"text": "Python 3.0 was released in 2008...", "metadata": {...}}
]

EXPECTED_ANSWER_INTERNAL_ONLY = "Python was created by Guido van Rossum [1]. Python 3.0 was released in 2008 [2]."

EXTERNAL_SUMMARIES = [
    {"summary": "Python is widely used in data science...", "citation": {"url": "https://..."}}
]
```

## Sequential Steps (TDD Approach)

Each step follows Red → Green → Refactor cycle with LLM-specific testing:

### 01 - Implement Synthesizer Chain

**Objective**: Create LangChain LLMChain that generates draft answers from internal passages with citations and signals when external info is needed

**Acceptance Criteria**:
- Chain accepts question and list of passages
- Output includes answer text with bracketed citations [1], [2]
- `needs_external` flag correctly detected from "MORE_INFO_NEEDED" marker
- Citations list preserves passage metadata
- Deterministic output with temperature=0
- Test: Verify citation format and flag detection with mocked LLM

**TDD Cycle**:
1. **Red**: Write test expecting synthesizer to return structured output with citations
2. **Green**: Implement chain with prompt template, LLM integration, parsing logic
3. **Refactor**: Extract citation formatting, improve prompt clarity, add error handling

**Files Modified**:
- Create: `chains/__init__.py`
- Create: `chains/synthesizer.py`
- Create: `tests/test_synthesizer_chain.py`
- Create: `tests/fixtures/qa_fixtures.py`

**Estimated Time**: 3-4 hours

---

### 02 - Implement External Summarizer Chain

**Objective**: Create LangChain LLMChain that consolidates multiple web page summaries into unified external information

**Acceptance Criteria**:
- Chain accepts list of summary dictionaries from Firecrawl
- Output combines summaries coherently without introducing new facts
- Citations preserved from input summaries
- External sources clearly distinguished
- Test: Verify summary consolidation and citation preservation with mocked LLM

**TDD Cycle**:
1. **Red**: Write test expecting summarizer to combine multiple summaries with citations
2. **Green**: Implement chain with prompt template and summary formatting
3. **Refactor**: Improve prompt to prevent hallucinations, optimize citation handling

**Files Modified**:
- Create: `chains/external_summarizer.py`
- Create: `tests/test_external_summarizer_chain.py`
- Update: `tests/fixtures/qa_fixtures.py` (add external summary fixtures)

**Estimated Time**: 2-3 hours

---

### 03 - Implement Critic Chain

**Objective**: Create LangChain LLMChain that merges internal and external content, resolves conflicts, and produces final answer with ordered citations

**Acceptance Criteria**:
- Chain accepts question, internal answer, and external summary
- Output integrates both sources coherently
- Citations ordered: internal [1], [2] then external [E1], [E2]
- Conflicts resolved with internal source priority
- Uncertain information explicitly noted
- Test: Verify conflict resolution and citation ordering with mocked LLM

**TDD Cycle**:
1. **Red**: Write test expecting critic to merge sources and order citations correctly
2. **Green**: Implement chain with conflict resolution prompt and citation merging
3. **Refactor**: Improve prompt for better conflict detection, validate citation ordering

**Files Modified**:
- Create: `chains/critic.py`
- Create: `tests/test_critic_chain.py`
- Update: `tests/fixtures/qa_fixtures.py` (add conflict scenarios)

**Estimated Time**: 3-4 hours

---

### 04 - Compose Workflow Orchestrator

**Objective**: Orchestrate retrieval, synthesizer, external search, and critic chains into cohesive workflow with conditional external search

**Acceptance Criteria**:
- Workflow accepts query and session context
- Internal retrieval always executed first
- External search triggered only when `needs_external=True`
- Critic receives both internal and external (if any) content
- Session memory updated after completion
- Response includes all required fields (answer, citations, links, etc.)
- Test: End-to-end workflow test with mocked LLM and retrieval tools

**TDD Cycle**:
1. **Red**: Write test expecting workflow to orchestrate all steps correctly
2. **Green**: Implement workflow with conditional logic and tool integration
3. **Refactor**: Extract configuration, add logging, improve error handling

**Files Modified**:
- Create: `workflows/__init__.py`
- Create: `workflows/answer_workflow.py`
- Create: `tests/test_answer_workflow.py`
- Update: `app/routes/query.py` (integrate workflow)

**Estimated Time**: 4-5 hours

---

## Commit Strategy

Following "Tidy First" methodology:

**Commit 1** (Step 01):
- Add synthesizer chain with prompt template
- Implement citation parsing and `needs_external` detection
- Tests for citation format and flag logic

**Commit 2** (Step 02):
- Add external summarizer chain
- Implement summary consolidation
- Tests for multi-source summarization

**Commit 3** (Step 03):
- Add critic chain with conflict resolution
- Implement citation ordering (internal first, external second)
- Tests for conflict scenarios

**Commit 4** (Step 04):
- Add workflow orchestrator
- Integrate all chains with conditional logic
- End-to-end integration tests

## Dependencies

- Feature F02: Document Ingestion (provides parsers and chunking)
- Feature F03: Vector Search RAG (retrieval tool)
- Feature F04: External Search (search tool and Firecrawl)
- Task 13: External page summarization must be complete
- LangChain installed: `pip install langchain langchain-openai`
- OpenAI API key configured in `.env`

## Blocks

- F06: Web UI depends on workflow endpoint being available
- Task 21: YouTube thumbnails will extend workflow response
- Task 22: Similar questions will extend workflow response

## Testing Prerequisites

Before starting, ensure:
1. Virtual environment activated with all dependencies
2. OpenAI API key set in `.env` file
3. Qdrant running and accessible (for integration tests)
4. Retrieval tool and external search tool from F03/F04 available
5. Test fixtures directory created (`tests/fixtures/`)
6. LangChain and OpenAI Python packages installed

## LLM Testing Best Practices

1. **Use Deterministic Settings**:
   - Set `temperature=0` for all test chains
   - Use fixed `random_seed` if provider supports it

2. **Mock External LLM Calls**:
   - Use `unittest.mock` to mock LLM responses in unit tests
   - Only call real LLM API in integration/acceptance tests

3. **Create Golden Datasets**:
   - Define expected outputs for known inputs
   - Use semantic similarity metrics (not exact string match)

4. **Test Edge Cases**:
   - Empty passages (no internal knowledge)
   - Contradictory sources (internal vs external conflict)
   - Missing external results (search returns nothing)
   - Very long answers (test token limits)

5. **Validate Citations**:
   - Assert all citations reference actual source passages
   - Check for hallucinated sources (citations without matching passages)
   - Verify citation numbering is sequential and consistent

6. **Handle Flakiness**:
   - Run LLM tests multiple times to detect flakiness
   - Use assertion ranges for semantic similarity (e.g., >0.8 threshold)
   - Log full LLM responses on test failures for debugging

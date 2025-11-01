# Step 01: Implement Synthesizer Chain

## Objective

Create a LangChain LLMChain that generates draft answers from internal knowledge base passages, includes proper citations in bracketed format [1], [2], and signals when external information is needed via a `needs_external` flag.

## Atomic Implementation

This step is atomic: it either creates a working synthesizer chain that produces cited answers and correctly detects information gaps, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected synthesizer behavior:

```python
# tests/test_synthesizer_chain.py
import pytest
from chains.synthesizer import run_synthesizer, SynthesizerOutput
from unittest.mock import Mock, patch

# Test fixtures
SAMPLE_PASSAGES = [
    {
        "text": "Python was created by Guido van Rossum in 1991.",
        "metadata": {"doc_id": "doc1", "filename": "python_history.pdf", "chunk_index": 0}
    },
    {
        "text": "Python 3.0 was released in December 2008, introducing major changes.",
        "metadata": {"doc_id": "doc1", "filename": "python_history.pdf", "chunk_index": 1}
    }
]

def test_synthesizer_returns_structured_output():
    """Test that synthesizer returns SynthesizerOutput with required fields."""
    question = "Who created Python?"

    # Mock LLM to return controlled response
    with patch("chains.synthesizer.synth_chain") as mock_chain:
        mock_chain.run.return_value = "Python was created by Guido van Rossum [1]."

        result = run_synthesizer(question, SAMPLE_PASSAGES)

        assert isinstance(result, SynthesizerOutput)
        assert isinstance(result.answer, str)
        assert isinstance(result.needs_external, bool)
        assert isinstance(result.citations, list)

def test_synthesizer_formats_citations_correctly():
    """Test that synthesizer includes bracketed citation numbers."""
    question = "When was Python 3.0 released?"

    with patch("chains.synthesizer.synth_chain") as mock_chain:
        mock_chain.run.return_value = "Python 3.0 was released in December 2008 [2]."

        result = run_synthesizer(question, SAMPLE_PASSAGES)

        assert "[2]" in result.answer
        assert result.needs_external is False

def test_synthesizer_detects_needs_external_flag():
    """Test that synthesizer correctly identifies when external info is needed."""
    question = "What is Python's current market share?"

    with patch("chains.synthesizer.synth_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Based on the provided passages, I don't have information about "
            "Python's current market share. MORE_INFO_NEEDED"
        )

        result = run_synthesizer(question, SAMPLE_PASSAGES)

        assert result.needs_external is True
        assert "MORE_INFO_NEEDED" not in result.answer  # Flag should be removed
        assert len(result.answer) > 0  # Answer should still have content

def test_synthesizer_preserves_passage_metadata():
    """Test that synthesizer returns citation metadata from passages."""
    question = "Tell me about Python."

    with patch("chains.synthesizer.synth_chain") as mock_chain:
        mock_chain.run.return_value = "Python was created by Guido van Rossum [1]."

        result = run_synthesizer(question, SAMPLE_PASSAGES)

        assert len(result.citations) == len(SAMPLE_PASSAGES)
        assert result.citations[0]["doc_id"] == "doc1"
        assert result.citations[0]["filename"] == "python_history.pdf"

def test_synthesizer_handles_empty_passages():
    """Test that synthesizer handles empty passage list gracefully."""
    question = "What is Python?"

    with patch("chains.synthesizer.synth_chain") as mock_chain:
        mock_chain.run.return_value = (
            "No passages provided to answer this question. MORE_INFO_NEEDED"
        )

        result = run_synthesizer(question, [])

        assert result.needs_external is True
        assert result.citations == []

def test_synthesizer_prompt_includes_passages():
    """Test that prompt template correctly formats passages."""
    question = "Who created Python?"

    with patch("chains.synthesizer.synth_chain") as mock_chain:
        mock_chain.run.return_value = "Python was created by Guido van Rossum [1]."

        run_synthesizer(question, SAMPLE_PASSAGES)

        # Verify run was called with formatted passages
        call_args = mock_chain.run.call_args
        assert call_args is not None
        assert "question" in call_args[1] or "question" in call_args[0]
        assert "passages" in call_args[1] or "passages" in call_args[0]

@pytest.mark.integration
def test_synthesizer_with_real_llm():
    """Integration test with actual LLM call (requires API key)."""
    import os
    if not os.getenv("MODEL_PROVIDER_API_KEY"):
        pytest.skip("MODEL_PROVIDER_API_KEY not set")

    question = "Who created Python and when?"
    result = run_synthesizer(question, SAMPLE_PASSAGES)

    # Verify answer quality with real LLM
    assert len(result.answer) > 20  # Substantial answer
    assert "Guido" in result.answer or "1991" in result.answer  # Contains info from passages
    assert "[1]" in result.answer or "[2]" in result.answer  # Has citations
```

**Expected Result**: All tests fail because `chains/synthesizer.py` doesn't exist yet.

### Green Phase

1. **Create chains module structure**:
   ```python
   # chains/__init__.py
   from .synthesizer import run_synthesizer, SynthesizerOutput

   __all__ = ["run_synthesizer", "SynthesizerOutput"]
   ```

2. **Implement synthesizer chain**:
   ```python
   # chains/synthesizer.py
   from langchain.prompts import PromptTemplate
   from langchain.chains import LLMChain
   from langchain_openai import OpenAI
   from pydantic import BaseModel
   import os

   # Data model for output
   class SynthesizerOutput(BaseModel):
       answer: str
       needs_external: bool
       citations: list[dict]

   # Prompt template
   synth_prompt = PromptTemplate(
       input_variables=["question", "passages"],
       template=(
           "You are a helpful assistant answering questions using provided passages."
           " Answer the question based only on these passages."
           " Cite each passage you use with a bracketed number in the order of appearance (e.g., [1], [2])."
           " If the information is insufficient, reply 'MORE_INFO_NEEDED' at the end.\n\n"
           "Question: {question}\n\n"
           "Passages:\n{passages}\n\n"
           "Answer:"
       ),
   )

   # Initialize LLM with deterministic settings
   llm = OpenAI(
       api_key=os.environ.get("MODEL_PROVIDER_API_KEY"),
       temperature=0  # Deterministic for testing
   )

   # Create chain
   synth_chain = LLMChain(llm=llm, prompt=synth_prompt)

   def run_synthesizer(question: str, passages: list[dict]) -> SynthesizerOutput:
       """Generate draft answer from internal passages with citations.

       Args:
           question: User's question
           passages: List of passage dictionaries with 'text' and 'metadata' keys

       Returns:
           SynthesizerOutput with answer, needs_external flag, and citations

       Example:
           >>> passages = [{"text": "Python was created in 1991...", "metadata": {...}}]
           >>> result = run_synthesizer("Who created Python?", passages)
           >>> print(result.answer)
           "Python was created by Guido van Rossum [1]."
           >>> print(result.needs_external)
           False
       """
       # Format passages as numbered list for prompt
       formatted_passages = format_passages(passages)

       # Call LLM chain
       answer = synth_chain.run(question=question, passages=formatted_passages)

       # Detect needs_external flag
       needs_external = answer.strip().endswith("MORE_INFO_NEEDED")

       # Remove flag from answer text
       if needs_external:
           answer = answer.replace("MORE_INFO_NEEDED", "").strip()

       # Extract citation metadata
       citations = [p["metadata"] for p in passages]

       return SynthesizerOutput(
           answer=answer,
           needs_external=needs_external,
           citations=citations
       )

   def format_passages(passages: list[dict]) -> str:
       """Format passages as numbered list for LLM prompt.

       Args:
           passages: List of passage dictionaries with 'text' key

       Returns:
           Formatted string with numbered passages

       Example:
           >>> passages = [{"text": "First passage"}, {"text": "Second passage"}]
           >>> print(format_passages(passages))
           [1] First passage
           [2] Second passage
       """
       if not passages:
           return "(No passages provided)"

       return "\n".join(
           [f"[{i+1}] {p['text']}" for i, p in enumerate(passages)]
       )
   ```

3. **Create test fixtures**:
   ```python
   # tests/fixtures/__init__.py
   from .qa_fixtures import SAMPLE_PASSAGES, SAMPLE_EXTERNAL_SUMMARIES

   __all__ = ["SAMPLE_PASSAGES", "SAMPLE_EXTERNAL_SUMMARIES"]
   ```

   ```python
   # tests/fixtures/qa_fixtures.py
   """Test fixtures for answer synthesis tests."""

   SAMPLE_PASSAGES = [
       {
           "text": "Python was created by Guido van Rossum in 1991.",
           "metadata": {
               "doc_id": "doc1",
               "filename": "python_history.pdf",
               "chunk_index": 0,
               "source": "upload"
           }
       },
       {
           "text": "Python 3.0 was released in December 2008, introducing major changes.",
           "metadata": {
               "doc_id": "doc1",
               "filename": "python_history.pdf",
               "chunk_index": 1,
               "source": "upload"
           }
       }
   ]

   SAMPLE_EXTERNAL_SUMMARIES = [
       {
           "summary": "Python is widely used in data science and machine learning.",
           "citation": {
               "url": "https://example.com/python-usage",
               "title": "Python Usage Statistics"
           }
       }
   ]
   ```

4. **Run tests**:
   ```bash
   pytest tests/test_synthesizer_chain.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add configuration for LLM settings**:
   ```python
   # chains/synthesizer.py
   from app.config import Config

   config = Config()

   llm = OpenAI(
       api_key=config.model_provider_api_key,
       temperature=config.llm_temperature,
       model=config.llm_model_name
   )
   ```

2. **Extract citation validation**:
   ```python
   # chains/synthesizer.py
   import re

   def validate_citations(answer: str, num_passages: int) -> bool:
       """Validate that citations in answer reference valid passage numbers.

       Args:
           answer: LLM-generated answer with citations
           num_passages: Number of passages provided

       Returns:
           True if all citations are valid, False otherwise
       """
       citation_pattern = r'\[(\d+)\]'
       cited_indices = [int(match) for match in re.findall(citation_pattern, answer)]

       # Check all citations are within valid range
       return all(1 <= idx <= num_passages for idx in cited_indices)

   def run_synthesizer(question: str, passages: list[dict]) -> SynthesizerOutput:
       # ... existing code ...

       # Validate citations
       if not validate_citations(answer, len(passages)):
           # Log warning but don't fail
           print(f"Warning: Answer contains invalid citation numbers")

       # ... rest of function
   ```

3. **Add error handling for LLM failures**:
   ```python
   # chains/synthesizer.py
   from tenacity import retry, stop_after_attempt, wait_exponential
   import logging

   logger = logging.getLogger(__name__)

   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=10),
       reraise=True
   )
   def call_llm_with_retry(chain: LLMChain, **kwargs) -> str:
       """Call LLM chain with exponential backoff retry.

       Args:
           chain: LangChain LLMChain instance
           **kwargs: Arguments to pass to chain.run()

       Returns:
           LLM response string

       Raises:
           Exception: If all retry attempts fail
       """
       try:
           return chain.run(**kwargs)
       except Exception as e:
           logger.error(f"LLM call failed: {e}")
           raise

   def run_synthesizer(question: str, passages: list[dict]) -> SynthesizerOutput:
       formatted_passages = format_passages(passages)

       try:
           answer = call_llm_with_retry(
               synth_chain,
               question=question,
               passages=formatted_passages
           )
       except Exception as e:
           logger.error(f"Synthesizer failed after retries: {e}")
           # Return fallback response
           return SynthesizerOutput(
               answer="I apologize, but I'm unable to generate an answer at this time.",
               needs_external=False,
               citations=[]
           )

       # ... rest of function
   ```

4. **Add logging for debugging**:
   ```python
   # chains/synthesizer.py
   def run_synthesizer(question: str, passages: list[dict]) -> SynthesizerOutput:
       logger.info(f"Synthesizer called with question: {question[:100]}...")
       logger.debug(f"Number of passages: {len(passages)}")

       formatted_passages = format_passages(passages)
       answer = call_llm_with_retry(synth_chain, question=question, passages=formatted_passages)

       needs_external = answer.strip().endswith("MORE_INFO_NEEDED")
       logger.debug(f"needs_external flag: {needs_external}")

       if needs_external:
           answer = answer.replace("MORE_INFO_NEEDED", "").strip()

       citations = [p["metadata"] for p in passages]

       logger.info(f"Synthesizer produced answer with {len(citations)} citations")
       return SynthesizerOutput(answer=answer, needs_external=needs_external, citations=citations)
   ```

5. **Update configuration**:
   ```python
   # app/config.py (update existing Config class)
   class Config(BaseSettings):
       # ... existing fields ...

       # LLM configuration
       llm_model_name: str = "gpt-3.5-turbo"
       llm_temperature: float = 0.0
       llm_max_tokens: int = 2000
   ```

6. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement synthesizer chain for RAG answers

   - Add SynthesizerChain with LangChain LLMChain
   - Implement prompt template with citation instructions
   - Add needs_external flag detection via MORE_INFO_NEEDED marker
   - Extract citation metadata from passages
   - Add citation validation and logging
   - Implement retry logic with exponential backoff
   - Add comprehensive unit tests with mocked LLM
   - Add integration test with real LLM (optional)

   Covers Task 14 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] SynthesizerChain accepts question and list of passages
- [x] Output includes answer text with bracketed citations [1], [2]
- [x] `needs_external` flag correctly detected from "MORE_INFO_NEEDED"
- [x] Flag removed from final answer text
- [x] Citation metadata preserved from input passages
- [x] Deterministic output with temperature=0
- [x] Citation validation checks for valid passage references
- [x] Error handling with retry logic for LLM failures
- [x] Logging for debugging and monitoring
- [x] Tests verify all scenarios (with/without external need, empty passages)

## Files Created/Modified

- Created: `chains/__init__.py`
- Created: `chains/synthesizer.py`
- Created: `tests/test_synthesizer_chain.py`
- Created: `tests/fixtures/__init__.py`
- Created: `tests/fixtures/qa_fixtures.py`
- Modified: `app/config.py` (add LLM configuration)

## Rollback Strategy

If this step fails:
1. Remove `chains/` directory
2. Remove `tests/test_synthesizer_chain.py`
3. Remove `tests/fixtures/qa_fixtures.py`
4. Run `git reset --hard HEAD~1`
5. Review error logs and fix issues
6. Retry step from Red phase

## Dependencies

Requires:
- LangChain installed: `pip install langchain langchain-openai`
- OpenAI API key in `.env` file: `MODEL_PROVIDER_API_KEY=sk-...`
- Tenacity for retry logic: `pip install tenacity`
- Pydantic for data models (already installed with FastAPI)

## Testing the Chain Manually

```python
# test_synthesizer_manual.py
from chains.synthesizer import run_synthesizer

passages = [
    {
        "text": "Python was created by Guido van Rossum in 1991.",
        "metadata": {"doc_id": "doc1", "filename": "test.pdf", "chunk_index": 0}
    },
    {
        "text": "Python 3.0 was released in December 2008.",
        "metadata": {"doc_id": "doc1", "filename": "test.pdf", "chunk_index": 1}
    }
]

# Test 1: Question with sufficient internal info
result = run_synthesizer("Who created Python?", passages)
print("Answer:", result.answer)
print("Needs External:", result.needs_external)
print("Citations:", len(result.citations))

# Test 2: Question requiring external info
result = run_synthesizer("What is Python's market share in 2024?", passages)
print("\nAnswer:", result.answer)
print("Needs External:", result.needs_external)
```

Run with:
```bash
python test_synthesizer_manual.py
```

## Next Step

Proceed to `02_external_summarizer_chain.md` - Implement chain to consolidate external web summaries

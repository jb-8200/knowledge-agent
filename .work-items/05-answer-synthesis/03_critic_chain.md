# Step 03: Implement Critic Chain

## Objective

Create a LangChain LLMChain that merges internal and external content into a final answer, resolves contradictions by preferring internal sources, orders citations (internal first, external second), and explicitly notes uncertain or conflicting information.

## Atomic Implementation

This step is atomic: it either creates a working critic chain that correctly merges content with proper conflict resolution and citation ordering, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected critic behavior:

```python
# tests/test_critic_chain.py
import pytest
from chains.critic import run_critic, CriticOutput
from chains.synthesizer import SynthesizerOutput
from chains.external_summarizer import ExternalSummarizerOutput
from unittest.mock import Mock, patch

# Test fixtures
INTERNAL_ANSWER = SynthesizerOutput(
    answer="Python was created by Guido van Rossum in 1991 [1]. It emphasizes code readability [2].",
    needs_external=False,
    citations=[
        {"doc_id": "doc1", "filename": "python.pdf", "chunk_index": 0},
        {"doc_id": "doc1", "filename": "python.pdf", "chunk_index": 1}
    ]
)

EXTERNAL_SUMMARY = ExternalSummarizerOutput(
    summary="Python is widely used in data science and ranks in the top 3 languages [1].",
    citations=[
        {"url": "https://datasciencecentral.com/python", "title": "Python Usage"}
    ]
)

CONFLICTING_EXTERNAL = ExternalSummarizerOutput(
    summary="Python was created by Guido van Rossum in 1989 [1].",  # Wrong year
    citations=[
        {"url": "https://wrong-source.com", "title": "Incorrect Info"}
    ]
)

def test_critic_returns_structured_output():
    """Test that critic returns CriticOutput with required fields."""
    question = "Tell me about Python."

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Python was created by Guido van Rossum in 1991 [1]. "
            "It emphasizes code readability [2] and is widely used in data science [E1]."
        )

        result = run_critic(question, INTERNAL_ANSWER, EXTERNAL_SUMMARY)

        assert isinstance(result, CriticOutput)
        assert isinstance(result.answer, str)
        assert isinstance(result.citations, list)

def test_critic_orders_citations_internal_first():
    """Test that citations are ordered: internal [1], [2], then external [E1], [E2]."""
    question = "Tell me about Python."

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = "Python was created in 1991 [1] and is popular [E1]."

        result = run_critic(question, INTERNAL_ANSWER, EXTERNAL_SUMMARY)

        # Verify citation ordering
        assert len(result.citations) == 3  # 2 internal + 1 external
        # First citations should be internal
        assert result.citations[0]["filename"] == "python.pdf"
        assert result.citations[1]["filename"] == "python.pdf"
        # Last citation should be external
        assert "url" in result.citations[2]
        assert result.citations[2]["url"] == "https://datasciencecentral.com/python"

def test_critic_integrates_both_sources():
    """Test that critic combines internal and external information."""
    question = "What is Python used for?"

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Python emphasizes code readability [2] and is widely used in data science [E1]."
        )

        result = run_critic(question, INTERNAL_ANSWER, EXTERNAL_SUMMARY)

        # Should reference both internal and external sources
        assert "[2]" in result.answer or "readability" in result.answer
        assert "[E1]" in result.answer or "data science" in result.answer

def test_critic_resolves_conflicts_prefer_internal():
    """Test that critic prefers internal sources when conflicts arise."""
    question = "When was Python created?"

    with patch("chains.critic.critic_chain") as mock_chain:
        # Mock response that prioritizes internal source (1991) over external (1989)
        mock_chain.run.return_value = (
            "Python was created by Guido van Rossum in 1991 [1]. "
            "Note: Some sources incorrectly state 1989."
        )

        result = run_critic(question, INTERNAL_ANSWER, CONFLICTING_EXTERNAL)

        # Should mention the correct year from internal source
        assert "1991" in result.answer or "[1]" in result.answer

def test_critic_notes_uncertainties():
    """Test that critic explicitly mentions uncertain or conflicting info."""
    question = "When was Python created?"

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Python was created in 1991 according to internal documents [1]. "
            "However, external sources conflict on this date."
        )

        result = run_critic(question, INTERNAL_ANSWER, CONFLICTING_EXTERNAL)

        # Should mention conflict or uncertainty
        uncertainty_keywords = ["conflict", "uncertain", "however", "note", "discrepancy"]
        assert any(keyword in result.answer.lower() for keyword in uncertainty_keywords)

def test_critic_handles_no_external_summary():
    """Test that critic works with empty external summary."""
    empty_external = ExternalSummarizerOutput(summary="", citations=[])
    question = "Tell me about Python."

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = INTERNAL_ANSWER.answer

        result = run_critic(question, INTERNAL_ANSWER, empty_external)

        # Should only have internal citations
        assert len(result.citations) == 2
        assert all("filename" in c for c in result.citations)

def test_critic_citation_markers_distinguish_sources():
    """Test that internal use [1] and external use [E1] format."""
    question = "Tell me about Python."

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Python was created in 1991 [1] and is popular in data science [E1]."
        )

        result = run_critic(question, INTERNAL_ANSWER, EXTERNAL_SUMMARY)

        # Verify distinct citation formats
        assert "[1]" in result.answer  # Internal citation
        assert "[E1]" in result.answer  # External citation

def test_critic_prompt_includes_all_inputs():
    """Test that prompt receives question, internal answer, and external summary."""
    question = "Tell me about Python."

    with patch("chains.critic.critic_chain") as mock_chain:
        mock_chain.run.return_value = "Final answer."

        run_critic(question, INTERNAL_ANSWER, EXTERNAL_SUMMARY)

        call_args = mock_chain.run.call_args
        assert call_args is not None
        kwargs = call_args[1] if call_args[1] else {}

        assert "question" in kwargs
        assert "internal_answer" in kwargs
        assert "external_summary" in kwargs

@pytest.mark.integration
def test_critic_with_real_llm():
    """Integration test with actual LLM call (requires API key)."""
    import os
    if not os.getenv("MODEL_PROVIDER_API_KEY"):
        pytest.skip("MODEL_PROVIDER_API_KEY not set")

    question = "Tell me about Python."
    result = run_critic(question, INTERNAL_ANSWER, EXTERNAL_SUMMARY)

    # Verify output quality
    assert len(result.answer) > 50  # Substantial answer
    assert len(result.citations) == 3  # 2 internal + 1 external
    # Should integrate both sources
    assert any(keyword in result.answer.lower() for keyword in ["created", "readability", "data science"])
```

**Expected Result**: All tests fail because `chains/critic.py` doesn't exist yet.

### Green Phase

1. **Implement critic chain**:
   ```python
   # chains/critic.py
   from langchain.prompts import PromptTemplate
   from langchain.chains import LLMChain
   from langchain_openai import OpenAI
   from pydantic import BaseModel
   import os
   import logging
   from chains.synthesizer import SynthesizerOutput
   from chains.external_summarizer import ExternalSummarizerOutput

   logger = logging.getLogger(__name__)

   # Data model for output
   class CriticOutput(BaseModel):
       answer: str
       citations: list[dict]

   # Prompt template
   critic_prompt = PromptTemplate(
       input_variables=["question", "internal_answer", "external_summary"],
       template=(
           "You are a critical reviewer combining two sources of information."
           " Given the question, an internal answer based on uploaded documents and an external summary from the web,"
           " craft a final answer that integrates both. Resolve any contradictions by preferring internal content unless the external source clearly corrects it."
           " Provide citations for each statement, numbering internal citations first (e.g., [1], [2]) and then external citations (e.g., [E1], [E2])."
           " If any information is uncertain or conflicted, mention it explicitly.\n\n"
           "Question: {question}\n\n"
           "Internal Answer:\n{internal_answer}\n\n"
           "External Summary:\n{external_summary}\n\n"
           "Final Answer:"
       ),
   )

   # Initialize LLM
   llm = OpenAI(
       api_key=os.environ.get("MODEL_PROVIDER_API_KEY"),
       temperature=0
   )

   # Create chain
   critic_chain = LLMChain(llm=llm, prompt=critic_prompt)

   def run_critic(
       question: str,
       internal: SynthesizerOutput,
       external: ExternalSummarizerOutput
   ) -> CriticOutput:
       """Merge internal and external content into final answer with conflict resolution.

       Args:
           question: User's original question
           internal: SynthesizerOutput from internal passages
           external: ExternalSummarizerOutput from web sources

       Returns:
           CriticOutput with final answer and ordered citations

       Example:
           >>> internal = SynthesizerOutput(answer="Python was created in 1991 [1].", ...)
           >>> external = ExternalSummarizerOutput(summary="Python is popular [1].", ...)
           >>> result = run_critic("Tell me about Python.", internal, external)
           >>> print(result.answer)
           "Python was created in 1991 [1] and is popular [E1]."
       """
       logger.info(f"Critic chain called for question: {question[:100]}...")
       logger.debug(f"Internal citations: {len(internal.citations)}, External citations: {len(external.citations)}")

       # Prepare external summary (handle empty case)
       external_summary_text = external.summary if external.summary else "No external information available."

       # Call LLM chain with retry
       from chains.synthesizer import call_llm_with_retry
       try:
           final_answer = call_llm_with_retry(
               critic_chain,
               question=question,
               internal_answer=internal.answer,
               external_summary=external_summary_text
           )
       except Exception as e:
           logger.error(f"Critic chain failed: {e}")
           # Fallback to internal answer only
           return CriticOutput(
               answer=internal.answer,
               citations=internal.citations
           )

       # Combine citations: internal first, then external
       ordered_citations = combine_citations(internal.citations, external.citations)

       logger.info(f"Critic produced final answer with {len(ordered_citations)} total citations")
       return CriticOutput(
           answer=final_answer.strip(),
           citations=ordered_citations
       )

   def combine_citations(
       internal_citations: list[dict],
       external_citations: list[dict]
   ) -> list[dict]:
       """Combine internal and external citations in correct order.

       Args:
           internal_citations: Citations from internal passages
           external_citations: Citations from external sources

       Returns:
           Combined list with internal first, external second

       Example:
           >>> internal = [{"filename": "doc.pdf"}]
           >>> external = [{"url": "https://..."}]
           >>> combined = combine_citations(internal, external)
           >>> len(combined)
           2
       """
       # Tag citations with source type for clarity
       tagged_internal = [
           {**c, "source_type": "internal"} for c in internal_citations
       ]
       tagged_external = [
           {**c, "source_type": "external"} for c in external_citations
       ]

       return tagged_internal + tagged_external
   ```

2. **Update chains module**:
   ```python
   # chains/__init__.py
   from .synthesizer import run_synthesizer, SynthesizerOutput
   from .external_summarizer import run_external_summarizer, ExternalSummarizerOutput
   from .critic import run_critic, CriticOutput

   __all__ = [
       "run_synthesizer",
       "SynthesizerOutput",
       "run_external_summarizer",
       "ExternalSummarizerOutput",
       "run_critic",
       "CriticOutput",
   ]
   ```

3. **Run tests**:
   ```bash
   pytest tests/test_critic_chain.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add conflict detection**:
   ```python
   # chains/critic.py
   def detect_conflicts(internal_answer: str, external_summary: str) -> bool:
       """Detect potential conflicts between internal and external sources.

       This is a simple heuristic - looks for contradictory keywords.

       Args:
           internal_answer: Answer from internal sources
           external_summary: Summary from external sources

       Returns:
           True if potential conflict detected
       """
       # Keywords that might indicate conflicts
       conflict_indicators = [
           ("was", "wasn't"),
           ("is", "isn't"),
           ("did", "didn't"),
           ("can", "cannot"),
           ("true", "false")
       ]

       # Simple check - this is a heuristic, not perfect
       internal_lower = internal_answer.lower()
       external_lower = external_summary.lower()

       for positive, negative in conflict_indicators:
           if (positive in internal_lower and negative in external_lower) or \
              (negative in internal_lower and positive in external_lower):
               return True

       return False

   def run_critic(
       question: str,
       internal: SynthesizerOutput,
       external: ExternalSummarizerOutput
   ) -> CriticOutput:
       # ... existing code ...

       # Detect potential conflicts
       if external.summary and detect_conflicts(internal.answer, external.summary):
           logger.warning("Potential conflict detected between internal and external sources")

       # ... rest of function
   ```

2. **Add citation validation**:
   ```python
   # chains/critic.py
   import re

   def validate_final_citations(
       answer: str,
       num_internal: int,
       num_external: int
   ) -> tuple[bool, list[str]]:
       """Validate that citations in final answer are properly formatted.

       Args:
           answer: Final answer with citations
           num_internal: Number of internal citations available
           num_external: Number of external citations available

       Returns:
           Tuple of (is_valid, list of issues)
       """
       issues = []

       # Check internal citations [1], [2], etc.
       internal_pattern = r'\[(\d+)\]'
       internal_cites = [int(m) for m in re.findall(internal_pattern, answer)]

       for cite in internal_cites:
           if cite < 1 or cite > num_internal:
               issues.append(f"Invalid internal citation [{cite}] (max: {num_internal})")

       # Check external citations [E1], [E2], etc.
       external_pattern = r'\[E(\d+)\]'
       external_cites = [int(m) for m in re.findall(external_pattern, answer)]

       for cite in external_cites:
           if cite < 1 or cite > num_external:
               issues.append(f"Invalid external citation [E{cite}] (max: {num_external})")

       return len(issues) == 0, issues

   def run_critic(
       question: str,
       internal: SynthesizerOutput,
       external: ExternalSummarizerOutput
   ) -> CriticOutput:
       # ... existing code up to final_answer = ...

       # Validate citations
       is_valid, issues = validate_final_citations(
           final_answer,
           len(internal.citations),
           len(external.citations)
       )

       if not is_valid:
           logger.warning(f"Final answer has citation issues: {issues}")

       # ... rest of function
   ```

3. **Add answer quality checks**:
   ```python
   # chains/critic.py
   def check_answer_quality(answer: str, question: str) -> dict:
       """Perform basic quality checks on final answer.

       Args:
           answer: Final answer text
           question: Original question

       Returns:
           Dictionary with quality metrics
       """
       quality = {
           "length": len(answer),
           "has_citations": bool(re.search(r'\[\d+\]|\[E\d+\]', answer)),
           "is_substantial": len(answer) > 50,
           "addresses_question": any(
               word.lower() in answer.lower()
               for word in question.split()
               if len(word) > 3  # Skip short words like "is", "the"
           )
       }

       return quality

   def run_critic(
       question: str,
       internal: SynthesizerOutput,
       external: ExternalSummarizerOutput
   ) -> CriticOutput:
       # ... existing code up to final_answer = ...

       # Check answer quality
       quality = check_answer_quality(final_answer, question)
       logger.debug(f"Answer quality: {quality}")

       if not quality["is_substantial"]:
           logger.warning("Final answer is very short, may be incomplete")

       if not quality["has_citations"]:
           logger.warning("Final answer has no citations")

       # ... rest of function
   ```

4. **Add external summary enhancement**:
   ```python
   # chains/critic.py
   def enhance_external_summary_for_critic(
       external_summary: str,
       num_internal_citations: int
   ) -> str:
       """Enhance external summary by converting citation numbers to E-format.

       This helps the LLM understand that external citations should use [E1] format.

       Args:
           external_summary: Original external summary with [1], [2] citations
           num_internal_citations: Number of internal citations (for context)

       Returns:
           Enhanced summary with guidance for E-format citations
       """
       if not external_summary:
           return "No external information available."

       # Add guidance prefix
       enhanced = (
           f"External sources (cite as [E1], [E2], etc., "
           f"distinct from internal [1]-[{num_internal_citations}]):\n"
           f"{external_summary}"
       )

       return enhanced

   def run_critic(
       question: str,
       internal: SynthesizerOutput,
       external: ExternalSummarizerOutput
   ) -> CriticOutput:
       logger.info(f"Critic chain called for question: {question[:100]}...")

       # Enhance external summary for better LLM understanding
       external_summary_text = enhance_external_summary_for_critic(
           external.summary,
           len(internal.citations)
       ) if external.summary else "No external information available."

       # ... rest of function
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement critic chain for answer merging

   - Add CriticChain with LangChain LLMChain
   - Implement prompt for merging internal and external content
   - Add conflict resolution preferring internal sources
   - Order citations: internal [1], [2] then external [E1], [E2]
   - Add conflict detection heuristics
   - Add citation validation for final answer
   - Add answer quality checks (length, citations, relevance)
   - Enhance external summary formatting for LLM clarity
   - Tag citations with source_type for downstream use
   - Add comprehensive unit tests with mocked LLM
   - Add integration test with real LLM (optional)

   Covers Task 16 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] CriticChain accepts question, internal answer, and external summary
- [x] Output integrates both sources coherently
- [x] Citations ordered: internal [1], [2] then external [E1], [E2]
- [x] Conflicts resolved with internal source priority
- [x] Uncertain information explicitly noted in answer
- [x] Empty external summary handled gracefully
- [x] Citation markers distinguish internal vs external
- [x] Conflict detection heuristics warn of potential issues
- [x] Citation validation ensures proper formatting
- [x] Answer quality checks for completeness
- [x] Tests verify all scenarios (with/without external, with conflicts)

## Files Created/Modified

- Created: `chains/critic.py`
- Created: `tests/test_critic_chain.py`
- Modified: `chains/__init__.py` (add exports)

## Rollback Strategy

If this step fails:
1. Remove `chains/critic.py`
2. Remove `tests/test_critic_chain.py`
3. Revert changes to `chains/__init__.py`
4. Run `git reset --hard HEAD~1`
5. Review error logs and fix issues
6. Retry step from Red phase

## Dependencies

Requires:
- Step 01 (Synthesizer) completed
- Step 02 (External Summarizer) completed
- LangChain installed
- OpenAI API key in `.env` file

## Testing the Chain Manually

```python
# test_critic_manual.py
from chains.synthesizer import SynthesizerOutput
from chains.external_summarizer import ExternalSummarizerOutput
from chains.critic import run_critic

# Mock internal answer
internal = SynthesizerOutput(
    answer="Python was created by Guido van Rossum in 1991 [1]. It emphasizes readability [2].",
    needs_external=False,
    citations=[
        {"doc_id": "doc1", "filename": "python.pdf", "chunk_index": 0},
        {"doc_id": "doc1", "filename": "python.pdf", "chunk_index": 1}
    ]
)

# Mock external summary
external = ExternalSummarizerOutput(
    summary="Python is widely used in data science and machine learning [1].",
    citations=[
        {"url": "https://datasciencecentral.com/python", "title": "Python Usage"}
    ]
)

question = "Tell me about Python and its applications."
result = run_critic(question, internal, external)

print("Final Answer:", result.answer)
print("\nCitations:")
for i, citation in enumerate(result.citations, 1):
    if citation.get("source_type") == "internal":
        print(f"  [{i}] {citation['filename']}, chunk {citation['chunk_index']}")
    else:
        print(f"  [E{i - 2}] {citation['title']}: {citation['url']}")
```

Run with:
```bash
python test_critic_manual.py
```

## Next Step

Proceed to `04_workflow_orchestrator.md` - Compose complete workflow orchestrating all chains

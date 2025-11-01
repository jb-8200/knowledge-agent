# Step 02: Implement External Summarizer Chain

## Objective

Create a LangChain LLMChain that consolidates multiple web page summaries from Firecrawl into a unified external information summary, preserving citations and ensuring no new information is introduced beyond what's in the source summaries.

## Atomic Implementation

This step is atomic: it either creates a working external summarizer that correctly consolidates summaries with citation preservation, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected external summarizer behavior:

```python
# tests/test_external_summarizer_chain.py
import pytest
from chains.external_summarizer import run_external_summarizer, ExternalSummarizerOutput
from unittest.mock import Mock, patch

# Test fixtures
SAMPLE_SUMMARIES = [
    {
        "summary": "Python is widely used in data science and machine learning applications.",
        "citation": {
            "url": "https://datasciencecentral.com/python-usage",
            "title": "Python Usage in Data Science"
        }
    },
    {
        "summary": "Python has consistently ranked in the top 3 programming languages since 2018.",
        "citation": {
            "url": "https://tiobe.com/index/python",
            "title": "TIOBE Index - Python"
        }
    },
    {
        "summary": "Python's syntax is designed to be readable and straightforward for beginners.",
        "citation": {
            "url": "https://python.org/about",
            "title": "About Python"
        }
    }
]

def test_external_summarizer_returns_structured_output():
    """Test that external summarizer returns ExternalSummarizerOutput."""
    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Python is widely used in data science [1] and ranks in the top 3 languages [2]."
        )

        result = run_external_summarizer(SAMPLE_SUMMARIES)

        assert isinstance(result, ExternalSummarizerOutput)
        assert isinstance(result.summary, str)
        assert isinstance(result.citations, list)

def test_external_summarizer_preserves_citations():
    """Test that summarizer preserves citation metadata from inputs."""
    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = "Python is popular in data science [1]."

        result = run_external_summarizer(SAMPLE_SUMMARIES)

        assert len(result.citations) == len(SAMPLE_SUMMARIES)
        assert result.citations[0]["url"] == "https://datasciencecentral.com/python-usage"
        assert result.citations[0]["title"] == "Python Usage in Data Science"

def test_external_summarizer_consolidates_multiple_summaries():
    """Test that summarizer combines multiple summaries coherently."""
    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = (
            "Python is widely used in data science and machine learning [1]. "
            "It has consistently ranked in the top 3 programming languages since 2018 [2]. "
            "Python's syntax is designed to be readable for beginners [3]."
        )

        result = run_external_summarizer(SAMPLE_SUMMARIES)

        # Should reference all sources
        assert "[1]" in result.summary
        assert "[2]" in result.summary
        assert "[3]" in result.summary
        assert len(result.summary) > 50  # Substantial combined summary

def test_external_summarizer_handles_single_summary():
    """Test that summarizer works with just one summary."""
    single_summary = [SAMPLE_SUMMARIES[0]]

    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = "Python is widely used in data science [1]."

        result = run_external_summarizer(single_summary)

        assert len(result.citations) == 1
        assert "[1]" in result.summary

def test_external_summarizer_handles_empty_summaries():
    """Test that summarizer handles empty summary list gracefully."""
    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = "No external information available."

        result = run_external_summarizer([])

        assert result.citations == []
        assert len(result.summary) > 0  # Should have some response

def test_external_summarizer_prompt_includes_summaries():
    """Test that prompt template correctly formats summaries."""
    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = "Combined summary."

        run_external_summarizer(SAMPLE_SUMMARIES)

        # Verify run was called with formatted summaries
        call_args = mock_chain.run.call_args
        assert call_args is not None
        assert "summaries" in call_args[1] or "summaries" in call_args[0]

def test_external_summarizer_citation_format():
    """Test that citation format matches expected structure."""
    with patch("chains.external_summarizer.external_chain") as mock_chain:
        mock_chain.run.return_value = "Python is popular [1]."

        result = run_external_summarizer(SAMPLE_SUMMARIES)

        # Verify citation structure
        for citation in result.citations:
            assert "url" in citation
            assert "title" in citation
            assert citation["url"].startswith("http")

@pytest.mark.integration
def test_external_summarizer_with_real_llm():
    """Integration test with actual LLM call (requires API key)."""
    import os
    if not os.getenv("MODEL_PROVIDER_API_KEY"):
        pytest.skip("MODEL_PROVIDER_API_KEY not set")

    result = run_external_summarizer(SAMPLE_SUMMARIES)

    # Verify output quality with real LLM
    assert len(result.summary) > 30  # Substantial summary
    assert len(result.citations) == 3  # All citations preserved
    # Should contain citation markers
    assert any(f"[{i}]" in result.summary for i in range(1, 4))
```

**Expected Result**: All tests fail because `chains/external_summarizer.py` doesn't exist yet.

### Green Phase

1. **Implement external summarizer chain**:
   ```python
   # chains/external_summarizer.py
   from langchain.prompts import PromptTemplate
   from langchain.chains import LLMChain
   from langchain_openai import OpenAI
   from pydantic import BaseModel
   import os
   import logging

   logger = logging.getLogger(__name__)

   # Data model for output
   class ExternalSummarizerOutput(BaseModel):
       summary: str
       citations: list[dict]

   # Prompt template
   external_prompt = PromptTemplate(
       input_variables=["summaries"],
       template=(
           "You are aggregating information from external sources."
           " Combine the following summaries into a coherent set of factual statements."
           " For each fact, include the citation number corresponding to the source summary in brackets."
           " Do not introduce any information not present in the summaries.\n\n"
           "Summaries:\n{summaries}\n\n"
           "Combined Summary:"
       ),
   )

   # Initialize LLM with deterministic settings
   llm = OpenAI(
       api_key=os.environ.get("MODEL_PROVIDER_API_KEY"),
       temperature=0  # Deterministic for testing
   )

   # Create chain
   external_chain = LLMChain(llm=llm, prompt=external_prompt)

   def run_external_summarizer(summaries: list[dict]) -> ExternalSummarizerOutput:
       """Consolidate multiple web page summaries into unified external information.

       Args:
           summaries: List of summary dictionaries with 'summary' and 'citation' keys

       Returns:
           ExternalSummarizerOutput with combined summary and citations

       Example:
           >>> summaries = [
           ...     {
           ...         "summary": "Python is popular in data science.",
           ...         "citation": {"url": "https://...", "title": "..."}
           ...     }
           ... ]
           >>> result = run_external_summarizer(summaries)
           >>> print(result.summary)
           "Python is popular in data science [1]."
           >>> print(len(result.citations))
           1
       """
       logger.info(f"External summarizer called with {len(summaries)} summaries")

       # Handle empty summaries
       if not summaries:
           logger.warning("No external summaries provided")
           return ExternalSummarizerOutput(
               summary="No external information available.",
               citations=[]
           )

       # Format summaries with indices for citations
       formatted_summaries = format_summaries(summaries)

       # Call LLM chain with retry
       from chains.synthesizer import call_llm_with_retry
       try:
           combined = call_llm_with_retry(
               external_chain,
               summaries=formatted_summaries
           )
       except Exception as e:
           logger.error(f"External summarizer failed: {e}")
           return ExternalSummarizerOutput(
               summary="Unable to summarize external sources at this time.",
               citations=[]
           )

       # Extract citation metadata
       citations = extract_citations(summaries)

       logger.info(f"External summarizer produced summary with {len(citations)} citations")
       return ExternalSummarizerOutput(
           summary=combined.strip(),
           citations=citations
       )

   def format_summaries(summaries: list[dict]) -> str:
       """Format summaries as numbered list for LLM prompt.

       Args:
           summaries: List of summary dictionaries with 'summary' key

       Returns:
           Formatted string with numbered summaries

       Example:
           >>> summaries = [{"summary": "First"}, {"summary": "Second"}]
           >>> print(format_summaries(summaries))
           [1] First
           [2] Second
       """
       return "\n".join(
           [f"[{i+1}] {s['summary']}" for i, s in enumerate(summaries)]
       )

   def extract_citations(summaries: list[dict]) -> list[dict]:
       """Extract citation metadata from summary list.

       Args:
           summaries: List of summary dictionaries with 'citation' key

       Returns:
           List of citation dictionaries with url and title

       Example:
           >>> summaries = [{"citation": {"url": "https://...", "title": "..."}}]
           >>> citations = extract_citations(summaries)
           >>> print(citations[0]["url"])
           "https://..."
       """
       return [s["citation"] for s in summaries]
   ```

2. **Update chains module**:
   ```python
   # chains/__init__.py
   from .synthesizer import run_synthesizer, SynthesizerOutput
   from .external_summarizer import run_external_summarizer, ExternalSummarizerOutput

   __all__ = [
       "run_synthesizer",
       "SynthesizerOutput",
       "run_external_summarizer",
       "ExternalSummarizerOutput",
   ]
   ```

3. **Update test fixtures**:
   ```python
   # tests/fixtures/qa_fixtures.py
   """Test fixtures for answer synthesis tests."""

   # ... existing SAMPLE_PASSAGES ...

   SAMPLE_EXTERNAL_SUMMARIES = [
       {
           "summary": "Python is widely used in data science and machine learning applications.",
           "citation": {
               "url": "https://datasciencecentral.com/python-usage",
               "title": "Python Usage in Data Science"
           }
       },
       {
           "summary": "Python has consistently ranked in the top 3 programming languages since 2018.",
           "citation": {
               "url": "https://tiobe.com/index/python",
               "title": "TIOBE Index - Python"
           }
       },
       {
           "summary": "Python's syntax is designed to be readable and straightforward for beginners.",
           "citation": {
               "url": "https://python.org/about",
               "title": "About Python"
           }
       }
   ]
   ```

4. **Run tests**:
   ```bash
   pytest tests/test_external_summarizer_chain.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add validation for summary structure**:
   ```python
   # chains/external_summarizer.py
   def validate_summary_structure(summaries: list[dict]) -> bool:
       """Validate that summaries have required structure.

       Args:
           summaries: List of summary dictionaries

       Returns:
           True if all summaries have 'summary' and 'citation' keys
       """
       required_keys = {"summary", "citation"}
       citation_keys = {"url", "title"}

       for s in summaries:
           if not required_keys.issubset(s.keys()):
               logger.warning(f"Summary missing required keys: {s.keys()}")
               return False
           if not citation_keys.issubset(s["citation"].keys()):
               logger.warning(f"Citation missing required keys: {s['citation'].keys()}")
               return False

       return True

   def run_external_summarizer(summaries: list[dict]) -> ExternalSummarizerOutput:
       logger.info(f"External summarizer called with {len(summaries)} summaries")

       if not summaries:
           logger.warning("No external summaries provided")
           return ExternalSummarizerOutput(summary="No external information available.", citations=[])

       # Validate structure
       if not validate_summary_structure(summaries):
           logger.error("Invalid summary structure")
           raise ValueError("Summaries must have 'summary' and 'citation' keys")

       # ... rest of function
   ```

2. **Add citation deduplication**:
   ```python
   # chains/external_summarizer.py
   def deduplicate_citations(citations: list[dict]) -> list[dict]:
       """Remove duplicate citations based on URL.

       Args:
           citations: List of citation dictionaries

       Returns:
           Deduplicated list of citations
       """
       seen_urls = set()
       unique_citations = []

       for citation in citations:
           url = citation.get("url")
           if url and url not in seen_urls:
               seen_urls.add(url)
               unique_citations.append(citation)
           elif not url:
               # Keep citations without URL (shouldn't happen but handle gracefully)
               unique_citations.append(citation)

       if len(unique_citations) < len(citations):
           logger.info(f"Deduplicated {len(citations) - len(unique_citations)} citations")

       return unique_citations

   def run_external_summarizer(summaries: list[dict]) -> ExternalSummarizerOutput:
       # ... existing code ...

       # Extract and deduplicate citations
       citations = extract_citations(summaries)
       citations = deduplicate_citations(citations)

       # ... rest of function
   ```

3. **Add citation count validation**:
   ```python
   # chains/external_summarizer.py
   import re

   def validate_citation_usage(summary: str, num_citations: int) -> bool:
       """Validate that citations in summary match available sources.

       Args:
           summary: Combined summary with citation markers
           num_citations: Number of available citations

       Returns:
           True if all citations are valid
       """
       citation_pattern = r'\[(\d+)\]'
       used_citations = [int(match) for match in re.findall(citation_pattern, summary)]

       # Check all citations are within valid range
       invalid_citations = [c for c in used_citations if c < 1 or c > num_citations]

       if invalid_citations:
           logger.warning(f"Summary contains invalid citations: {invalid_citations}")
           return False

       return True

   def run_external_summarizer(summaries: list[dict]) -> ExternalSummarizerOutput:
       # ... existing code up to combined = ...

       # Validate citation usage
       if not validate_citation_usage(combined, len(citations)):
           logger.warning("Summary contains invalid citation numbers")

       logger.info(f"External summarizer produced summary with {len(citations)} citations")
       return ExternalSummarizerOutput(summary=combined.strip(), citations=citations)
   ```

4. **Add summary length limits**:
   ```python
   # chains/external_summarizer.py
   MAX_SUMMARY_LENGTH = 1000  # characters

   def truncate_summary(summary: str, max_length: int = MAX_SUMMARY_LENGTH) -> str:
       """Truncate summary to maximum length at sentence boundary.

       Args:
           summary: Combined summary text
           max_length: Maximum allowed length in characters

       Returns:
           Truncated summary ending at sentence boundary
       """
       if len(summary) <= max_length:
           return summary

       # Find last sentence boundary before max_length
       truncated = summary[:max_length]
       last_period = truncated.rfind('.')
       last_exclaim = truncated.rfind('!')
       last_question = truncated.rfind('?')

       boundary = max(last_period, last_exclaim, last_question)

       if boundary > 0:
           return summary[:boundary + 1]
       else:
           # No sentence boundary found, hard truncate
           return summary[:max_length] + "..."

   def run_external_summarizer(summaries: list[dict]) -> ExternalSummarizerOutput:
       # ... existing code up to combined = ...

       # Truncate if needed
       if len(combined) > MAX_SUMMARY_LENGTH:
           logger.warning(f"Summary exceeds max length ({len(combined)} > {MAX_SUMMARY_LENGTH}), truncating")
           combined = truncate_summary(combined)

       # ... rest of function
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement external summarizer chain for CAG

   - Add ExternalSummarizerChain with LangChain LLMChain
   - Implement prompt template for multi-source consolidation
   - Preserve citation metadata (URLs and titles)
   - Add summary structure validation
   - Add citation deduplication by URL
   - Add citation usage validation
   - Implement summary length limits with truncation
   - Add comprehensive unit tests with mocked LLM
   - Add integration test with real LLM (optional)

   Covers Task 15 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] ExternalSummarizerChain accepts list of summary dictionaries
- [x] Output combines multiple summaries coherently
- [x] Citations preserved with url and title metadata
- [x] Citation markers [1], [2] correspond to source summaries
- [x] No new information introduced beyond input summaries
- [x] Empty summary list handled gracefully
- [x] Summary structure validation (required keys)
- [x] Citation deduplication by URL
- [x] Citation usage validation (no invalid numbers)
- [x] Summary length limits with sentence-boundary truncation
- [x] Tests verify all scenarios (single, multiple, empty summaries)

## Files Created/Modified

- Created: `chains/external_summarizer.py`
- Created: `tests/test_external_summarizer_chain.py`
- Modified: `chains/__init__.py` (add exports)
- Modified: `tests/fixtures/qa_fixtures.py` (add external summary fixtures)

## Rollback Strategy

If this step fails:
1. Remove `chains/external_summarizer.py`
2. Remove `tests/test_external_summarizer_chain.py`
3. Revert changes to `chains/__init__.py`
4. Run `git reset --hard HEAD~1`
5. Review error logs and fix issues
6. Retry step from Red phase

## Dependencies

Requires:
- Step 01 (Synthesizer) completed (reuses retry logic)
- LangChain installed: `pip install langchain langchain-openai`
- OpenAI API key in `.env` file
- Task 13 (Firecrawl integration) for external summary source

## Testing the Chain Manually

```python
# test_external_summarizer_manual.py
from chains.external_summarizer import run_external_summarizer

summaries = [
    {
        "summary": "Python is widely used in data science and machine learning.",
        "citation": {
            "url": "https://datasciencecentral.com/python",
            "title": "Python in Data Science"
        }
    },
    {
        "summary": "Python has consistently ranked in the top 3 programming languages.",
        "citation": {
            "url": "https://tiobe.com/python",
            "title": "TIOBE Index"
        }
    }
]

result = run_external_summarizer(summaries)
print("Combined Summary:", result.summary)
print("\nCitations:")
for i, citation in enumerate(result.citations, 1):
    print(f"  [{i}] {citation['title']}: {citation['url']}")
```

Run with:
```bash
python test_external_summarizer_manual.py
```

## Next Step

Proceed to `03_critic_chain.md` - Implement chain to merge internal and external content with conflict resolution

# TDD Workflow Skill

This skill provides deep expertise in Test-Driven Development methodology, specifically tailored for the knowledge-agent project.

## When to Activate

This skill should be active when:
- Implementing a new feature or step
- Writing tests before implementation
- Refactoring existing code
- Debugging test failures
- Improving test coverage

## TDD Fundamentals

### The Three Phases

**🔴 RED Phase**: Write a failing test
- Define expected behavior through tests
- Test should fail for the right reason (not implemented yet)
- Use descriptive test names that explain what is being tested
- One assertion per test when possible

**🟢 GREEN Phase**: Make the test pass with minimal code
- Write simplest code to pass the test
- Don't worry about optimization yet
- Don't add features not covered by tests
- Confirm test passes before moving on

**🔵 REFACTOR Phase**: Improve code quality while keeping tests green
- Extract functions, remove duplication
- Improve names, add documentation
- Optimize performance if needed
- Run tests after each refactoring step

### The Cycle

```
RED → GREEN → REFACTOR → RED (next test) → ...
```

## Testing Best Practices for This Project

### Test Organization

```
tests/
├── test_upload_endpoint.py    # API endpoint tests
├── test_parsers.py             # Document parser tests
├── test_chunker.py             # Text chunking tests
├── test_embeddings.py          # Embedding generation tests
├── test_vector_store.py        # Qdrant integration tests
├── test_artifacts.py           # Artifact storage tests
├── test_pipeline.py            # End-to-end pipeline tests
└── fixtures/                   # Test data
    ├── sample.pdf
    ├── sample.docx
    └── sample.md
```

### Test Naming Convention

```python
def test_{component}_{scenario}():
    """Test that {component} {expected behavior} when {scenario}."""
    pass

# Examples:
def test_upload_pdf_returns_ingestion_id():
    """Test that uploading a valid PDF returns an ingestion ID."""

def test_parse_pdf_extracts_text_from_all_pages():
    """Test that PDF parser extracts text from all pages."""

def test_chunker_respects_max_chunk_size():
    """Test that chunker creates chunks within size limits."""
```

### Test Structure (AAA Pattern)

```python
def test_example():
    # ARRANGE: Set up test data and dependencies
    sample_text = "This is a test document."
    expected_chunks = 1

    # ACT: Execute the code being tested
    result = chunk_text(sample_text, doc_id="test", filename="test.txt")

    # ASSERT: Verify expected outcomes
    assert len(result) == expected_chunks
    assert result[0].text == sample_text
    assert result[0].metadata["doc_id"] == "test"
```

### Mocking External Dependencies

```python
import pytest
from unittest.mock import Mock, patch

def test_firecrawl_integration_with_mock():
    """Test URL ingestion with mocked Firecrawl."""
    # ARRANGE
    mock_response = {
        "success": True,
        "data": {"markdown": "# Test Content"}
    }

    # ACT: Mock the external service
    with patch('ingestion.firecrawl_client.FirecrawlApp') as mock_fc:
        mock_fc.return_value.scrape.return_value = mock_response
        result = ingest_url("https://example.com")

    # ASSERT
    assert result["status"] == "success"
    mock_fc.return_value.scrape.assert_called_once()
```

### Fixture Management

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_pdf_path():
    """Provide path to sample PDF fixture."""
    return Path(__file__).parent / "fixtures" / "sample.pdf"

@pytest.fixture
def sample_text():
    """Provide sample text for chunking tests."""
    return "This is a sample document. " * 100

def test_parse_pdf_uses_fixture(sample_pdf_path):
    """Test PDF parsing with fixture."""
    result = parse_pdf(str(sample_pdf_path))
    assert len(result) > 0
```

## Project-Specific TDD Guidance

### For API Endpoints

1. **RED**: Write request/response tests
   - Test valid inputs return 200/201
   - Test invalid inputs return 400/422
   - Test error conditions return 500/503
   - Test response structure matches specification

2. **GREEN**: Implement minimal endpoint
   - Create route with FastAPI decorator
   - Add request validation (Pydantic models)
   - Return basic response structure
   - Add error handlers

3. **REFACTOR**: Improve endpoint quality
   - Extract validation logic to helper functions
   - Add comprehensive error messages
   - Add logging at appropriate levels
   - Add type hints and docstrings

### For Data Processing Functions

1. **RED**: Write transformation tests
   - Test happy path with typical input
   - Test edge cases (empty, very large, malformed)
   - Test error handling for invalid inputs
   - Test output format and structure

2. **GREEN**: Implement transformation
   - Handle main use case first
   - Add basic error checking
   - Return correct output structure

3. **REFACTOR**: Enhance robustness
   - Add input validation
   - Improve error messages
   - Optimize performance if needed
   - Add logging for debugging

### For Integration Components

1. **RED**: Write integration tests
   - Test component communicates with external service
   - Test error handling when service unavailable
   - Test retry logic for transient failures
   - Test data format conversions

2. **GREEN**: Implement integration
   - Create client or wrapper class
   - Add basic error handling
   - Implement core functionality

3. **REFACTOR**: Production-ready integration
   - Add connection pooling if applicable
   - Add comprehensive retry logic
   - Add timeout handling
   - Add circuit breaker pattern if needed
   - Add detailed logging

## Common TDD Anti-Patterns to Avoid

### ❌ Don't: Write implementation before tests
```python
# BAD: Implementing first
def parse_pdf(file_path):
    # ... 50 lines of code ...

# Then writing tests after
def test_parse_pdf():
    result = parse_pdf("test.pdf")
    assert result  # Vague assertion
```

### ✅ Do: Write test first
```python
# GOOD: Test first defines expected behavior
def test_parse_pdf_extracts_text():
    """Test that PDF parser extracts text from all pages."""
    # RED: This test will fail
    result = parse_pdf("tests/fixtures/sample.pdf")
    assert "expected text content" in result
    assert len(result) > 100  # Should extract meaningful content

# Then implement to make it pass
def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)
```

### ❌ Don't: Test implementation details
```python
# BAD: Testing internal implementation
def test_chunker_uses_recursive_splitter():
    """This test is too coupled to implementation."""
    chunker = TextChunker()
    assert isinstance(chunker.splitter, RecursiveCharacterTextSplitter)
```

### ✅ Do: Test observable behavior
```python
# GOOD: Testing what the function does, not how
def test_chunker_creates_overlapping_passages():
    """Test that chunker creates passages with specified overlap."""
    text = "word " * 500
    chunks = chunk_text(text, chunk_size=100, overlap=20)

    # Verify overlap by checking adjacent chunks
    assert chunks[0].text[-20:] == chunks[1].text[:20]
```

### ❌ Don't: Write tests that depend on each other
```python
# BAD: Tests have hidden dependencies
def test_01_create_document():
    global doc_id
    doc_id = create_document()

def test_02_search_document():
    # Depends on test_01 running first
    result = search(doc_id)
    assert result
```

### ✅ Do: Make tests independent
```python
# GOOD: Each test stands alone
@pytest.fixture
def sample_document():
    """Create a test document (fresh for each test)."""
    doc_id = create_document()
    yield doc_id
    delete_document(doc_id)  # Cleanup

def test_create_document():
    """Test document creation."""
    doc_id = create_document()
    assert doc_id is not None
    delete_document(doc_id)

def test_search_document(sample_document):
    """Test document search."""
    result = search(sample_document)
    assert result is not None
```

## TDD Workflow for This Project

### Starting a New Step

1. Read the step file (e.g., `01_file_upload_endpoint.md`)
2. Identify "RED Phase" test examples
3. Create test file: `tests/test_{feature}.py`
4. Run: `pytest tests/test_{feature}.py -v` (should fail)
5. Implement minimal code to pass tests
6. Run tests again (should pass)
7. Refactor and improve
8. Commit with descriptive message

### During Development

- **Commit after GREEN**: When tests pass
- **Commit after REFACTOR**: When quality improved
- **Run full suite frequently**: `pytest tests/ -v`
- **Check coverage**: `pytest --cov=app --cov=ingestion`

### Before Completing a Step

1. All step tests passing: ✅
2. Full test suite passing: ✅
3. Coverage > 80%: ✅
4. No TODO comments: ✅
5. Type hints complete: ✅
6. Docstrings present: ✅
7. Use `/verify-step` to confirm

## Pytest Configuration

The project uses pytest with these plugins:

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-v",                          # Verbose output
    "--tb=short",                  # Short traceback format
    "--strict-markers",            # Enforce marker registration
    "--cov=app",                   # Coverage for app
    "--cov=ingestion",             # Coverage for ingestion
    "--cov-report=term-missing",   # Show missing lines
]
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parsers.py -v

# Run specific test
pytest tests/test_parsers.py::test_parse_pdf_extracts_text -v

# Run with coverage
pytest tests/ --cov=app --cov=ingestion --cov-report=html

# Run failed tests only
pytest --lf -v

# Run in parallel (if pytest-xdist installed)
pytest -n auto tests/
```

## Debugging Test Failures

### Use verbose output and print statements
```python
def test_example():
    result = some_function()
    print(f"Result: {result}")  # Will show in pytest output with -s flag
    assert result == expected

# Run with: pytest tests/test_file.py::test_example -v -s
```

### Use pytest debugging
```python
import pytest

def test_example():
    result = some_function()
    pytest.set_trace()  # Debugger breakpoint
    assert result == expected

# Or use: pytest --pdb tests/test_file.py
```

### Check fixtures
```python
def test_with_fixture_inspection(sample_data):
    print(f"Fixture value: {sample_data}")
    print(f"Fixture type: {type(sample_data)}")
    # ... rest of test
```

## Remember

- **Red → Green → Refactor** is not optional, it's the discipline
- **Tests are documentation** - they show how the code should be used
- **Failing tests are progress** - they define what needs to be built
- **Passing tests give confidence** - refactor without fear
- **Fast feedback is essential** - run tests constantly

This skill helps you maintain rigorous TDD discipline throughout the knowledge-agent project, ensuring high quality and maintainable code.

# Step 01: Initialize Repository and Virtual Environment

## Objective

Create the Git repository, Python virtual environment, and install all foundational dependencies for the knowledge-base agent.

## Atomic Implementation

This step is atomic: it either completes fully (repo + venv + packages) or fails entirely.

## TDD Cycle

### Red Phase

Write a failing test that expects all packages to be importable:

```python
# tests/test_setup.py
import pytest

def test_core_dependencies_importable():
    """Verify all core dependencies can be imported."""
    try:
        import langchain
        import firecrawl
        import qdrant_client
        import fastapi
        import uvicorn
        import dotenv
        from sentence_transformers import SentenceTransformer
        import tavily
    except ImportError as e:
        pytest.fail(f"Failed to import core dependency: {e}")

def test_langchain_version():
    """Ensure LangChain version is compatible."""
    import langchain
    assert hasattr(langchain, '__version__')
```

**Expected Result**: Test fails because packages aren't installed yet.

### Green Phase

1. **Initialize Git repository**:
   ```bash
   git init
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

2. **Create `.gitignore`**:
   ```gitignore
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   venv/
   env/
   .venv/

   # Environment
   .env
   .env.local

   # IDEs
   .vscode/
   .idea/
   *.swp

   # Artifacts
   artifacts/
   *.log

   # OS
   .DS_Store
   Thumbs.db

   # Frontend
   node_modules/
   dist/
   ```

3. **Create directory structure**:
   ```bash
   mkdir -p app ingestion frontend tests evals docs scripts
   touch app/__init__.py ingestion/__init__.py tests/__init__.py
   ```

4. **Create Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Create `requirements.txt`**:
   ```
   # Core Framework
   langchain>=0.1.0
   langgraph>=0.0.20

   # Web & Document Processing
   firecrawl-py>=0.0.5
   pdfplumber>=0.10.0
   python-docx>=1.1.0
   markdown>=3.5.0

   # Vector Database
   qdrant-client>=1.7.0

   # API Server
   fastapi>=0.109.0
   uvicorn[standard]>=0.27.0

   # ML & Embeddings
   sentence-transformers>=2.2.2

   # Search
   tavily-python>=0.2.0

   # Utilities
   python-dotenv>=1.0.0
   tenacity>=8.2.0

   # Development
   pytest>=7.4.0
   pytest-asyncio>=0.21.0
   black>=23.0.0
   ruff>=0.1.0
   mypy>=1.8.0
   ```

6. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. **Run test**:
   ```bash
   pytest tests/test_setup.py::test_core_dependencies_importable -v
   ```

**Expected Result**: Test passes.

### Refactor Phase

1. **Organize requirements.txt** with clear sections
2. **Add README.md** with setup instructions
3. **Create initial commit**:
   ```bash
   git add .
   git commit -m "chore: initialize repository and development environment

   - Create Python virtual environment
   - Add core dependencies (LangChain, Firecrawl, Qdrant, FastAPI)
   - Set up directory structure for app, ingestion, tests
   - Add .gitignore for Python, env files, and artifacts

   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] Git repository exists with initial commit
- [x] Virtual environment activates without errors
- [x] All packages install successfully (no dependency conflicts)
- [x] Test `test_core_dependencies_importable` passes
- [x] Directory structure matches design specification
- [x] `requirements.txt` lists all dependencies with versions

## Files Created/Modified

- Created: `.gitignore`
- Created: `requirements.txt`
- Created: `README.md`
- Created: `app/__init__.py`, `ingestion/__init__.py`, `tests/__init__.py`
- Created: `tests/test_setup.py`
- Created: `.git/` (repository)

## Rollback Strategy

If this step fails:
1. Delete `venv/` directory
2. Run `git reset --hard HEAD` (if committed)
3. Investigate dependency conflicts
4. Retry with adjusted requirements.txt

## Next Step

Proceed to `02_create_env.md` - Create environment configuration template

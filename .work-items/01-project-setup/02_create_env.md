# Step 02: Create Environment Configuration

## Objective

Set up environment variable management using `.env` template and python-dotenv, with type-safe configuration loading.

## Atomic Implementation

This step creates a complete configuration system that either works fully or fails clearly.

## TDD Cycle

### Red Phase

Write failing tests for configuration loading:

```python
# tests/test_config.py
import pytest
import os
from app.config import Config, get_config

def test_config_loads_from_env(monkeypatch):
    """Test that Config loads values from environment variables."""
    monkeypatch.setenv("QDRANT_URL", "http://test:6333")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("MODEL_PROVIDER_API_KEY", "test-key-123")

    config = get_config()
    assert config.qdrant_url == "http://test:6333"
    assert config.llm_provider == "openai"
    assert config.model_api_key == "test-key-123"

def test_config_has_defaults():
    """Test that Config provides sensible defaults for optional values."""
    config = get_config()
    assert config.qdrant_url == "http://localhost:6333"  # default
    assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert config.log_level == "INFO"

def test_config_validates_required_fields():
    """Test that missing required fields raise clear errors."""
    # This will fail until we implement validation
    with pytest.raises(ValueError, match="MODEL_PROVIDER_API_KEY"):
        config = Config(model_api_key=None)
```

**Expected Result**: Tests fail because `app/config.py` doesn't exist yet.

### Green Phase

1. **Create `.env.template`** (for version control):
   ```bash
   # .env.template
   # Copy this file to .env and fill in your values

   # LLM Provider Configuration
   LLM_PROVIDER=local
   # Options: 'local', 'openai', 'anthropic', 'google'

   MODEL_PROVIDER_API_KEY=your_api_key_here
   # Get from: OpenAI, Anthropic, or Google AI Studio

   # Embedding Model
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   # Local model, no API key required

   # Vector Store (Qdrant)
   QDRANT_URL=http://localhost:6333
   QDRANT_API_KEY=
   # Leave blank for local Qdrant; required for Qdrant Cloud

   # Web Search
   SEARCH_API_KEY=your_tavily_key_here
   # Get from: https://tavily.com

   # Firecrawl (Web Scraping)
   FIRECRAWL_API_KEY=your_firecrawl_key_here
   # Get from: https://firecrawl.dev

   # YouTube Data API (for thumbnails)
   YOUTUBE_API_KEY=your_youtube_key_here
   # Get from: https://console.cloud.google.com

   # Application Settings
   DEBUG=true
   LOG_LEVEL=INFO
   # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
   ```

2. **Create `app/config.py`** with type-safe configuration:
   ```python
   # app/config.py
   """Application configuration management.

   Loads settings from environment variables with validation and defaults.
   """
   from typing import Optional, Literal
   from pydantic import BaseSettings, validator
   import os
   from dotenv import load_dotenv

   # Load .env file if it exists
   load_dotenv()

   class Config(BaseSettings):
       """Application configuration from environment variables."""

       # LLM Configuration
       llm_provider: Literal["local", "openai", "anthropic", "google"] = "local"
       model_api_key: Optional[str] = None

       # Embedding Configuration
       embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

       # Vector Store
       qdrant_url: str = "http://localhost:6333"
       qdrant_api_key: Optional[str] = None

       # External Services
       search_api_key: Optional[str] = None
       firecrawl_api_key: Optional[str] = None
       youtube_api_key: Optional[str] = None

       # Application
       debug: bool = False
       log_level: str = "INFO"

       class Config:
           env_file = ".env"
           case_sensitive = False

       @validator("model_api_key")
       def validate_api_key_if_not_local(cls, v, values):
           """Require API key for non-local providers."""
           if values.get("llm_provider") != "local" and not v:
               raise ValueError(
                   f"MODEL_PROVIDER_API_KEY required for provider: {values.get('llm_provider')}"
               )
           return v

   # Singleton pattern for config
   _config_instance: Optional[Config] = None

   def get_config() -> Config:
       """Get or create the application configuration singleton."""
       global _config_instance
       if _config_instance is None:
           _config_instance = Config()
       return _config_instance
   ```

3. **Update `app/__init__.py`** to expose config:
   ```python
   # app/__init__.py
   """Knowledge-base agent application."""
   from .config import get_config, Config

   __all__ = ["get_config", "Config"]
   ```

4. **Run tests**:
   ```bash
   pytest tests/test_config.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add type hints and docstrings** to all functions
2. **Add logging** to config loading:
   ```python
   import logging

   logger = logging.getLogger(__name__)

   def get_config() -> Config:
       global _config_instance
       if _config_instance is None:
           _config_instance = Config()
           logger.info(f"Loaded config: provider={_config_instance.llm_provider}, qdrant={_config_instance.qdrant_url}")
       return _config_instance
   ```

3. **Create user documentation** in `README.md`:
   ```markdown
   ## Setup

   1. Copy environment template:
      ```bash
      cp .env.template .env
      ```

   2. Edit `.env` and add your API keys

   3. Activate virtual environment:
      ```bash
      source venv/bin/activate
      ```

   4. Verify setup:
      ```python
      from app import get_config
      config = get_config()
      print(config.qdrant_url)
      ```
   ```

4. **Commit**:
   ```bash
   git add .
   git commit -m "feat: add environment configuration management

   - Create .env.template with all required config keys
   - Implement type-safe Config class using Pydantic
   - Add validation for required API keys based on provider
   - Add singleton pattern for config access
   - Tests verify config loading and defaults

   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] `.env.template` exists with all configuration keys documented
- [x] `app/config.py` loads environment variables using python-dotenv
- [x] Config class provides type hints and validation
- [x] Missing required keys raise ValueError with clear message
- [x] Optional keys have sensible defaults
- [x] Tests verify config loading and validation
- [x] `.env` is in `.gitignore` (from previous step)

## Files Created/Modified

- Created: `.env.template`
- Created: `app/config.py`
- Created: `tests/test_config.py`
- Modified: `app/__init__.py`
- Modified: `README.md`

## Rollback Strategy

If this step fails:
1. Remove `app/config.py`
2. Remove `.env.template`
3. Run `git reset --hard HEAD~1`
4. Fix errors and retry

## Dependencies

Requires:
- `python-dotenv` (installed in step 01)
- `pydantic` (add to requirements.txt if missing)

## Next Feature

Feature complete! Proceed to next feature:
- **F02: document-ingestion** - `.work-items/02-document-ingestion/`

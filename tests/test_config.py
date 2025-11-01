"""Test application configuration management."""

import pytest
import os
from unittest.mock import patch


def test_config_loads_from_env(monkeypatch):
    """Test that Config loads values from environment variables."""
    from app import reset_config

    # Reset singleton before test
    reset_config()

    monkeypatch.setenv("QDRANT_URL", "http://test:6333")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-key-123")

    from app.config import get_config

    config = get_config()
    assert config.qdrant_url == "http://test:6333"
    assert config.llm_provider == "openai"
    assert config.llm_api_key == "test-key-123"


def test_config_has_defaults():
    """Test that Config provides sensible defaults for optional values."""
    from app import reset_config

    # Reset singleton before test
    reset_config()

    # Clear environment to test defaults
    with patch.dict(os.environ, {}, clear=True):
        from app.config import Config

        config = Config()
        assert config.qdrant_url == "http://localhost:6333"  # default
        assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.log_level == "INFO"


def test_config_validates_required_fields():
    """Test that validation works for provider-specific requirements."""
    from app import reset_config
    from app.config import Config

    # Reset singleton before test
    reset_config()

    # Should fail when using non-local provider without API key
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        Config(llm_provider="openai", llm_api_key=None)

    # Should succeed with local provider and no API key
    config = Config(llm_provider="local", llm_api_key=None)
    assert config.llm_provider == "local"

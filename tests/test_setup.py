"""Test core project dependencies are properly installed."""

import pytest


def test_core_dependencies_importable():
    """Verify all core dependencies can be imported.

    This test ensures that the essential packages required for the
    knowledge-agent system are installed and importable.

    Red Phase: This test will fail initially because dependencies
    are not yet installed.
    """
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


def test_python_version():
    """Verify Python version meets minimum requirements (3.10+)."""
    import sys

    version_info = sys.version_info
    assert version_info >= (3, 10), (
        f"Python 3.10+ required, found {version_info.major}.{version_info.minor}"
    )

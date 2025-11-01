"""Application configuration management.

Loads settings from environment variables with validation and defaults.
Uses Pydantic Settings for type-safe configuration.
"""

import logging
from typing import Optional, Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load .env file if it exists
load_dotenv()


class Config(BaseSettings):
    """Application configuration from environment variables.

    All configuration is loaded from environment variables or .env file.
    Provides type safety, validation, and sensible defaults.
    """

    # LLM Configuration
    llm_provider: Literal["local", "openai", "anthropic", "google"] = "local"
    llm_api_key: Optional[str] = None

    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector Store
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # External Services
    search_api_key: Optional[str] = None
    firecrawl_api_key: Optional[str] = None
    youtube_api_key: Optional[str] = None

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    # Upload Configuration
    max_upload_size: int = 10 * 1024 * 1024  # 10MB default
    upload_temp_dir: str = "/tmp/kb_uploads"

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
        protected_namespaces=(),  # Disable protected namespace warnings
    )

    @field_validator("llm_api_key")
    @classmethod
    def validate_api_key_if_not_local(cls, v: Optional[str], info) -> Optional[str]:
        """Require API key for non-local LLM providers.

        Args:
            v: The llm_api_key value
            info: Validation context containing other field values

        Returns:
            The validated API key

        Raises:
            ValueError: If non-local provider is used without an API key
        """
        # Access other field values from info.data
        llm_provider = info.data.get("llm_provider")

        if llm_provider != "local" and not v:
            raise ValueError(
                f"LLM_API_KEY required for provider: {llm_provider}"
            )
        return v


# Singleton pattern for config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the application configuration singleton.

    This ensures configuration is loaded only once and reused throughout
    the application lifecycle.

    Returns:
        Config: The application configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
        logger.info(
            f"Loaded configuration: "
            f"provider={_config_instance.llm_provider}, "
            f"qdrant={_config_instance.qdrant_url}, "
            f"embedding={_config_instance.embedding_model}"
        )
    return _config_instance


def reset_config() -> None:
    """Reset the configuration singleton.

    This is primarily used for testing to ensure a clean state between tests.
    Should not be called in production code.
    """
    global _config_instance
    _config_instance = None

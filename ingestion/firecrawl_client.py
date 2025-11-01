"""Firecrawl client wrapper for web content extraction."""

import logging
from typing import Dict, Any
from firecrawl import FirecrawlApp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.config import get_config

logger = logging.getLogger(__name__)


class FirecrawlClient:
    """Wrapper for Firecrawl API with error handling."""

    def __init__(self, api_key: str):
        """Initialize Firecrawl client."""
        self.client = FirecrawlApp(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL with automatic retry on transient failures.

        Retries up to 3 times with exponential backoff for connection and timeout errors.

        Args:
            url: The URL to scrape

        Returns:
            Dict containing scraped content with 'success', 'data' keys

        Raises:
            Exception: If scraping fails after all retries
        """
        logger.info(f"Scraping URL: {url}")
        try:
            result = self.client.scrape_url(url)

            # Validate response has expected structure
            if not isinstance(result, dict):
                raise ValueError(f"Unexpected response type: {type(result)}")

            content = result.get("content", "")
            markdown = result.get("markdown", "")

            # Ensure we got some content
            if not content and not markdown:
                logger.warning(f"No content extracted from {url}")

            return {
                "success": True,
                "data": {
                    "content": content,
                    "markdown": markdown,
                }
            }
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Transient error scraping {url}: {e} - will retry")
            raise
        except Exception as e:
            logger.error(f"Firecrawl scraping failed for {url}: {e}")
            raise


def get_firecrawl_client() -> FirecrawlClient:
    """Get a configured Firecrawl client instance."""
    config = get_config()
    return FirecrawlClient(api_key=config.firecrawl_api_key)

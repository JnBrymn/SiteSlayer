"""
HTTP fetching utilities
"""

import requests
import time
from typing import Optional
from contextlib import contextmanager
from utils.logger import setup_logger
from config import USER_AGENT

logger = setup_logger(__name__)

# Default HTTP headers for requests
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    # Removed Accept-Encoding to avoid binary/compressed response issues
    # requests will still handle decompression automatically if needed
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def fetch_page(url: str, config, max_retries: int = 3) -> Optional[str]:
    """
    Fetch a web page and return its HTML content
    
    Args:
        url: URL to fetch
        config: Configuration object
        max_retries: Maximum number of retry attempts for transient failures
        
    Returns:
        HTML content or None if failed
    """
    # Use JavaScript rendering if enabled
    if getattr(config, 'use_js_rendering', False):
        return fetch_page_with_js(url, config)
    
    # Build headers with user agent
    headers = DEFAULT_HEADERS.copy()
    headers['User-Agent'] = USER_AGENT
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=config.timeout,
                allow_redirects=True
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type.lower():
                logger.warning(f"Non-HTML content type for {url}: {content_type}")
                return None
            
            # Ensure proper encoding - if not detected, default to utf-8
            if response.encoding is None:
                response.encoding = 'utf-8'
            
            return response.text
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
                
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP {status_code} error fetching {url}")
            
            # Don't retry client errors (4xx), only server errors (5xx)
            if 400 <= status_code < 500:
                return None
            elif attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}", exc_info=True)
            return None
    
    return None


@contextmanager
def _create_browser(config):
    """
    Context manager for creating and properly closing a Playwright browser instance
    
    Args:
        config: Configuration object
        
    Yields:
        Playwright browser instance
    """
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    
    try:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        
        try:
            yield context
        finally:
            context.close()
            browser.close()
    finally:
        playwright.stop()


def fetch_page_with_js(url: str, config) -> Optional[str]:
    """
    Fetch a web page using Playwright to execute JavaScript
    
    Args:
        url: URL to fetch
        config: Configuration object
        
    Returns:
        Rendered HTML content or None if failed
    """
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright._impl._errors import Error as PlaywrightError
    except ImportError:
        logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        logger.info("Falling back to regular HTTP fetch")
        # Fall back to regular fetch without modifying config
        return fetch_page(url, config, max_retries=1)
    
    try:
        logger.info(f"Fetching with JavaScript rendering: {url}")
        
        with _create_browser(config) as context:
            page = context.new_page()
            
            try:
                # Navigate to the URL and wait for load
                page.goto(url, wait_until='networkidle', timeout=config.timeout * 1000)
                
                # Additional wait for JavaScript execution if configured
                js_wait_time = getattr(config, 'js_wait_time', 3)
                if js_wait_time > 0:
                    time.sleep(js_wait_time)
                
                # Get the fully rendered HTML
                html_content = page.content()
                
                logger.info(f"Successfully fetched with JS rendering: {url}")
                return html_content
            finally:
                page.close()
            
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout fetching with JavaScript {url}: {str(e)}")
        return None
    except PlaywrightError as e:
        error_msg = str(e)
        if "Executable doesn't exist" in error_msg or "BrowserType.launch" in error_msg:
            logger.error(f"Playwright browser not installed. Please run: playwright install chromium")
            logger.error(f"Error details: {error_msg}")
        else:
            logger.error(f"Playwright error fetching with JavaScript {url}: {error_msg}")
        return None
    except Exception as e:
        logger.error(f"Error fetching with JavaScript {url}: {str(e)}", exc_info=True)
        return None


def create_session(config) -> requests.Session:
    """
    Create a requests Session with default headers for reuse across multiple requests
    
    Args:
        config: Configuration object
        
    Returns:
        Configured requests Session object
    """
    session = requests.Session()
    
    headers = DEFAULT_HEADERS.copy()
    headers['User-Agent'] = USER_AGENT
    session.headers.update(headers)
    
    return session

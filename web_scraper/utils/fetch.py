"""
HTTP fetching utilities
"""

import time
import asyncio
import aiohttp
from typing import Optional
from contextlib import contextmanager
from utils.logger import setup_logger
from config import USER_AGENT

logger = setup_logger(__name__)

# Browser pool for Playwright reuse
_browser_pool = None
_browser_lock = asyncio.Lock()

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


async def _fetch_page_http(url: str, config, max_retries: int = 3) -> Optional[str]:
    """
    Fetch a web page using HTTP requests (fallback when JS rendering unavailable)
    
    Args:
        url: URL to fetch
        config: Configuration object
        max_retries: Maximum number of retry attempts for transient failures
        
    Returns:
        HTML content or None if failed
    """
    # Build headers with user agent
    headers = DEFAULT_HEADERS.copy()
    headers['User-Agent'] = USER_AGENT
    
    # Use reduced timeout (4 seconds) if we've already hit a timeout for this site
    effective_timeout = 4 if getattr(config, 'timeout_reduced', False) else config.timeout
    
    # Retry logic with exponential backoff
    timeout = aiohttp.ClientTimeout(total=effective_timeout)
    
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        for attempt in range(max_retries):
            try:
                async with session.get(url, allow_redirects=True) as response:
                    # Check if request was successful
                    if response.status >= 400:
                        status_code = response.status
                        logger.error(f"HTTP {status_code} error fetching {url}")
                        
                        # Don't retry client errors (4xx), only server errors (5xx)
                        if 400 <= status_code < 500:
                            return None
                        elif attempt < max_retries - 1:
                            wait_time = 2 ** attempt
                            logger.info(f"Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            return None
                    
                    # Check content type
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' not in content_type.lower():
                        logger.warning(f"Non-HTML content type for {url}: {content_type}")
                        return None
                    
                    # Read content with proper encoding
                    html_content = await response.text(encoding='utf-8')
                    return html_content
                    
            except asyncio.TimeoutError:
                # Mark config to use reduced timeout for subsequent pages
                if not getattr(config, 'timeout_reduced', False):
                    config.timeout_reduced = True
                    logger.info(f"Site appears slow - reducing timeout to 4 seconds for remaining pages")
                logger.error(f"Timeout fetching {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    return None
                    
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}", exc_info=True)
                return None
        
        return None


async def fetch_page(url: str, config, max_retries: int = 3) -> Optional[str]:
    """
    Fetch a web page and return its HTML content using JavaScript rendering
    
    Args:
        url: URL to fetch
        config: Configuration object
        max_retries: Maximum number of retry attempts for transient failures
        
    Returns:
        HTML content or None if failed
    """
    return await fetch_page_with_js(url, config)


async def get_browser_instance():
    """
    Get or create a shared browser instance (singleton pattern with async lock)
    
    Returns:
        dict: Dictionary with 'playwright' and 'browser' keys, or None if failed
    """
    global _browser_pool
    
    async with _browser_lock:
        if _browser_pool is None:
            try:
                from playwright.async_api import async_playwright
                
                logger.info("Initializing Playwright browser pool...")
                playwright = await async_playwright().start()
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                    ]
                )
                _browser_pool = {
                    'playwright': playwright,
                    'browser': browser
                }
                logger.info("Browser pool initialized successfully")
            except ImportError:
                logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize browser pool: {str(e)}", exc_info=True)
                return None
        
        return _browser_pool


async def cleanup_browser_pool():
    """
    Clean up the browser pool when done with all scraping operations.
    Should be called when all fetching is complete.
    """
    global _browser_pool
    
    async with _browser_lock:
        if _browser_pool:
            try:
                logger.info("Cleaning up browser pool...")
                await _browser_pool['browser'].close()
                await _browser_pool['playwright'].stop()
                _browser_pool = None
                logger.info("Browser pool cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up browser pool: {str(e)}", exc_info=True)
                _browser_pool = None


async def fetch_page_with_js(url: str, config) -> Optional[str]:
    """
    Fetch a web page using Playwright to execute JavaScript.
    Reuses a shared browser instance for better performance.
    
    Args:
        url: URL to fetch
        config: Configuration object
        
    Returns:
        Rendered HTML content or None if failed
    """
    try:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright._impl._errors import Error as PlaywrightError
    except ImportError:
        logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        logger.info("Falling back to regular HTTP fetch")
        # Fall back to regular HTTP fetch without modifying config
        return await _fetch_page_http(url, config, max_retries=1)
    
    # Get shared browser instance
    pool = await get_browser_instance()
    if not pool:
        logger.warning("Browser pool unavailable, falling back to regular HTTP fetch")
        return await _fetch_page_http(url, config, max_retries=1)
    
    browser = pool['browser']
    timeout_occurred = False
    
    # Use reduced timeout (4 seconds) if we've already hit a timeout for this site
    effective_timeout = 4 if getattr(config, 'timeout_reduced', False) else config.timeout
    
    try:
        logger.info(f"Fetching with JavaScript rendering: {url}")
        
        # Create a new context for each request (isolates cookies/cache)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        
        try:
            page = await context.new_page()
            
            try:
                # Navigate to the URL and wait for load
                try:
                    await page.goto(url, wait_until='networkidle', timeout=effective_timeout * 1000)
                except PlaywrightTimeoutError as e:
                    timeout_occurred = True
                    # Mark config to use reduced timeout for subsequent pages
                    if not getattr(config, 'timeout_reduced', False):
                        config.timeout_reduced = True
                        logger.info(f"Site appears slow - reducing timeout to 4 seconds for remaining pages")
                    logger.warning(f"Timeout waiting for networkidle on {url}: {str(e)}")
                    logger.info("Attempting to capture partial HTML content that has already loaded...")
                    # Don't re-raise - we'll try to get whatever content is available
                
                # Additional wait for JavaScript execution if configured (only if no timeout)
                if not timeout_occurred:
                    js_wait_time = getattr(config, 'js_wait_time', 3)
                    if js_wait_time > 0:
                        await asyncio.sleep(js_wait_time)
                
                # Get the rendered HTML (even if timeout occurred)
                try:
                    html_content = await page.content()
                    if timeout_occurred:
                        logger.warning(f"Retrieved partial HTML content: {len(html_content)} characters (timeout occurred)")
                    else:
                        logger.info(f"Successfully fetched with JS rendering: {url}")
                    return html_content
                except Exception as e:
                    logger.error(f"Failed to retrieve HTML content even after timeout: {str(e)}", exc_info=True)
                    return None  # If we can't even get the content, that's a real failure
            finally:
                await page.close()
        finally:
            await context.close()
            
    except PlaywrightTimeoutError as e:
        # This catch is for any timeout that wasn't caught above (shouldn't happen, but safety net)
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

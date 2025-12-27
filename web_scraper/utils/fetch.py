"""
HTTP fetching utilities
"""

import asyncio
from utils.logger import setup_logger

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


"""
HTTP fetching utilities
"""

import requests
import time
from typing import Optional
from contextlib import contextmanager
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Default HTTP headers for requests
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
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
    headers['User-Agent'] = config.user_agent
    
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


def _configure_chrome_options(config) -> 'Options':
    """
    Configure Chrome options for headless browsing
    
    Args:
        config: Configuration object
        
    Returns:
        Configured Chrome Options object
    """
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    
    # Basic headless configuration
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # User agent and stealth settings
    chrome_options.add_argument(f'user-agent={config.user_agent}')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Additional performance and stability options
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    
    return chrome_options


@contextmanager
def _create_webdriver(config):
    """
    Context manager for creating and properly closing a WebDriver instance
    
    Args:
        config: Configuration object
        
    Yields:
        WebDriver instance
    """
    from selenium import webdriver
    
    chrome_options = _configure_chrome_options(config)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.set_page_load_timeout(config.timeout)
        yield driver
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Error closing WebDriver: {str(e)}")


def fetch_page_with_js(url: str, config) -> Optional[str]:
    """
    Fetch a web page using Selenium to execute JavaScript
    
    Args:
        url: URL to fetch
        config: Configuration object
        
    Returns:
        Rendered HTML content or None if failed
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
    except ImportError:
        logger.error("Selenium not installed. Install with: pip install selenium")
        logger.info("Falling back to regular HTTP fetch")
        # Fall back to regular fetch without modifying config
        return fetch_page(url, config, max_retries=1)
    
    try:
        logger.info(f"Fetching with JavaScript rendering: {url}")
        
        with _create_webdriver(config) as driver:
            # Navigate to the URL
            driver.get(url)
            
            # Wait for the document to be ready
            try:
                WebDriverWait(driver, config.timeout).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except Exception as e:
                logger.warning(f"Document ready state check failed: {str(e)}")
            
            # Additional wait for JavaScript execution if configured
            js_wait_time = getattr(config, 'js_wait_time', 3)
            if js_wait_time > 0:
                time.sleep(js_wait_time)
            
            # Get the fully rendered HTML
            html_content = driver.page_source
            
            logger.info(f"Successfully fetched with JS rendering: {url}")
            return html_content
            
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
    headers['User-Agent'] = config.user_agent
    session.headers.update(headers)
    
    return session

"""
HTTP fetching utilities
"""

import requests
from utils.logger import setup_logger

logger = setup_logger(__name__)

def fetch_page(url, config):
    """
    Fetch a web page and return its HTML content
    
    Args:
        url (str): URL to fetch
        config (Config): Configuration object
        
    Returns:
        str: HTML content or None if failed
    """
    headers = {
        'User-Agent': config.user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
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
        logger.error(f"Timeout fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {str(e)}", exc_info=True)
        return None

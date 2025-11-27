"""
Link filtering and cleaning utilities
"""

from urllib.parse import urlparse, urljoin
from utils.logger import setup_logger

logger = setup_logger(__name__)

def clean_and_filter_links(links, base_url, config):
    """
    Clean and filter links based on various criteria
    
    Args:
        links (list[str]): List of URL strings
        base_url (str): Base URL of the site
        config (Config): Configuration object
        
    Returns:
        list[str]: Filtered and cleaned URLs
    """
    base_domain = urlparse(base_url).netloc
    seen_urls = set()
    filtered_links = []
    
    for url in links:
        # Parse URL first to normalize it (remove fragment)
        parsed = urlparse(url)
        
        # Only keep links from the same domain
        if parsed.netloc != base_domain:
            continue
        
        # Skip links with excluded extensions
        if any(url.lower().endswith(ext) for ext in config.exclude_extensions):
            continue
        
        # Remove fragment but keep query params
        # This ensures URLs that differ only by hash are treated as the same
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
        
        # Skip if cleaned URL was already seen (this catches hash-only duplicates)
        if clean_url in seen_urls:
            continue
        
        seen_urls.add(clean_url)
        
        filtered_links.append(clean_url)
    
    return filtered_links

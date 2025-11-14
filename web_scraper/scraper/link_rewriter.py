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
        links (list): List of link dictionaries with 'url' and 'text'
        base_url (str): Base URL of the site
        config (Config): Configuration object
        
    Returns:
        list: Filtered and cleaned links
    """
    base_domain = urlparse(base_url).netloc
    seen_urls = set()
    filtered_links = []
    
    for link in links:
        url = link['url']
        
        # Skip if already seen
        if url in seen_urls:
            continue
        
        # Parse URL
        parsed = urlparse(url)
        
        # Only keep links from the same domain
        if parsed.netloc != base_domain:
            continue
        
        # Skip links with excluded extensions
        if any(url.lower().endswith(ext) for ext in config.exclude_extensions):
            continue
        
        # Skip query parameters and fragments (optional)
        # Remove fragment but keep query params
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
        
        # Skip if cleaned URL was already seen
        if clean_url in seen_urls:
            continue
        
        seen_urls.add(clean_url)
        
        filtered_links.append({
            'url': clean_url,
            'text': link['text']
        })
    
    return filtered_links

def is_valid_url(url):
    """Check if URL is valid and accessible"""
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

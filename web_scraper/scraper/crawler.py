"""
Site crawler - Navigates through website links and scrapes content
"""

import asyncio
import hashlib
import threading
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils.fetch import fetch_page
from utils.logger import setup_logger
from scraper.markdown_converter import html_to_markdown

logger = setup_logger(__name__)

def normalize_url(url):
    """
    Normalize URL by removing fragment (hash) to ensure uniqueness
    URLs that differ only by hash are treated as the same
    """
    parsed = urlparse(url)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        clean_url += f"?{parsed.query}"
    return clean_url

def _process_single_url(url, index, total, visited_urls, visited_lock, config):
    """
    Process a single URL - extracted for parallel processing
    
    Args:
        url: URL to process
        index: Index of this URL in the list (for logging)
        total: Total number of URLs
        visited_urls: Set of visited URLs (thread-safe access via lock)
        visited_lock: Lock for thread-safe access to visited_urls
        config: Configuration object
        
    Returns:
        dict: Page data if successful, None otherwise
    """
    # Normalize URL (remove fragment) to check for duplicates
    normalized_url = normalize_url(url)
    
    # Check and mark as visited (thread-safe)
    with visited_lock:
        if normalized_url in visited_urls:
            return None
        visited_urls.add(normalized_url)
    
    logger.info(f"[{index}/{total}] Scraping: {url}")
    
    try:
        # Fetch page
        html_content = fetch_page(url, config)
        if not html_content:
            logger.warning(f"Failed to fetch: {url}")
            return None
        
        # Parse and extract content
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract title
        title = soup.title.string if soup.title else "No title"
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
            element.decompose()
        
        # Find main content
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'id': 'content'}) or
            soup.find('div', {'class': ['content', 'main-content', 'post-content']}) or
            soup.find('body')
        )
        
        if not main_content:
            logger.warning(f"No main content found for: {url}")
            return None
        
        # Convert to markdown
        markdown_content = html_to_markdown(str(main_content), url)
        
        # Check minimum content length
        if len(markdown_content) < config.min_content_length:
            logger.info(f"Content too short, skipping: {url}")
            return None
        
        # Save page
        page_data = {
            'url': url,
            'title': title,
            'content': markdown_content
        }
        
        save_page(page_data, config)
        return page_data
        
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}", exc_info=True)
        return None


async def crawl_urls(links_to_crawl, config):
    """
    Crawl URLs from the provided list of links in parallel
    
    Args:
        links_to_crawl (list[str]): List of URL strings to crawl (already ranked/processed)
        config (Config): Configuration object
        
    Returns:
        list: List of scraped page data
    """
    visited_urls = set()
    visited_lock = threading.Lock()  # Thread-safe lock for visited_urls set
    results = []
    
    logger.info(f"Starting crawl of {len(links_to_crawl)} links (max concurrent: {config.max_concurrent_requests})")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(config.max_concurrent_requests)
    
    async def process_with_semaphore(url, index):
        """Wrapper to process URL with semaphore control"""
        async with semaphore:
            # Run the sync processing function in a thread
            result = await asyncio.to_thread(
                _process_single_url,
                url,
                index,
                len(links_to_crawl),
                visited_urls,
                visited_lock,
                config
            )
            return result
    
    # Create tasks for all URLs
    tasks = [
        process_with_semaphore(url, i + 1)
        for i, url in enumerate(links_to_crawl)
    ]
    
    # Process all tasks and collect results
    task_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results and exceptions
    for result in task_results:
        if isinstance(result, Exception):
            logger.error(f"Task raised exception: {str(result)}", exc_info=True)
        elif result is not None:
            results.append(result)
    
    logger.info(f"Crawl complete. Successfully scraped {len(results)} pages")
    return results

def save_page(page_data, config):
    """Save page content to file"""
    try:
        # Create file content first
        content = f"# {page_data['title']}\n\n"
        content += f"Source: {page_data['url']}\n"
        content += "\n---\n\n"
        content += page_data['content']
        
        # Hash content to MD5
        md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Create filename from MD5 hash
        filename = f"{md5_hash}.md"
        filepath = config.output_dir / filename
        
        # Save file (overwrites if it already exists)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.debug(f"Saved: {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving page {page_data['url']}: {str(e)}", exc_info=True)

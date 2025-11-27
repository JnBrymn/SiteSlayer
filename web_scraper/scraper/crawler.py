"""
Site crawler - Navigates through website links and scrapes content
"""

import time
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

def crawl_urls(base_url, links_to_crawl, config):
    """
    Crawl URLs from the provided list of links
    
    Args:
        base_url (str): Base URL of the site
        links_to_crawl (list[str]): List of URL strings to crawl (already ranked/processed)
        config (Config): Configuration object
        
    Returns:
        list: List of scraped page data
    """
    visited_urls = set()
    results = []
    base_domain = urlparse(base_url).netloc
    
    logger.info(f"Starting crawl of {len(links_to_crawl)} links")
    
    for i, url in enumerate(links_to_crawl, 1):
        # Normalize URL (remove fragment) to check for duplicates
        normalized_url = normalize_url(url)
        
        # Skip if already visited (using normalized URL)
        if normalized_url in visited_urls:
            continue
        
        visited_urls.add(normalized_url)
        
        logger.info(f"[{i}/{len(links_to_crawl)}] Scraping: {url}")
        
        try:
            # Fetch page
            html_content = fetch_page(url, config)
            if not html_content:
                logger.warning(f"Failed to fetch: {url}")
                continue
            
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
                continue
            
            # Convert to markdown
            markdown_content = html_to_markdown(str(main_content), url)
            
            # Check minimum content length
            if len(markdown_content) < config.min_content_length:
                logger.info(f"Content too short, skipping: {url}")
                continue
            
            # Save page
            page_data = {
                'url': url,
                'title': title,
                'content': markdown_content
            }
            
            save_page(page_data, base_domain, config)
            results.append(page_data)
            
            # Delay between requests
            if i < len(links_to_crawl):
                time.sleep(config.delay_between_requests)
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}", exc_info=True)
            continue
    
    logger.info(f"Crawl complete. Successfully scraped {len(results)} pages")
    return results

def save_page(page_data, base_domain, config):
    """Save page content to file"""
    try:
        # Create safe filename from URL
        url_path = urlparse(page_data['url']).path
        if not url_path or url_path == '/':
            filename = "index.md"
        else:
            # Clean path and create filename
            clean_path = url_path.strip('/').replace('/', '_').replace('\\', '_')
            # Limit filename length
            if len(clean_path) > 100:
                clean_path = clean_path[:100]
            filename = f"{clean_path}.md"
        
        filepath = config.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_data['title']}\n\n")
            f.write(f"Source: {page_data['url']}\n")
            f.write("\n---\n\n")
            f.write(page_data['content'])
        
        logger.debug(f"Saved: {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving page {page_data['url']}: {str(e)}", exc_info=True)

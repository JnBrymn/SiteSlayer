"""
Site crawler - Navigates through website links and scrapes content
"""

import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils.fetch import fetch_page
from utils.logger import setup_logger
from scraper.markdown_converter import html_to_markdown
from scraper.ai_link_ranker import rank_links

logger = setup_logger(__name__)

def crawl_site(base_url, initial_links, config):
    """
    Crawl the site starting from initial links
    
    Args:
        base_url (str): Base URL of the site
        initial_links (list): List of links to start crawling
        config (Config): Configuration object
        
    Returns:
        list: List of scraped page data
    """
    visited_urls = set()
    results = []
    base_domain = urlparse(base_url).netloc
    
    # Rank links if AI ranking is enabled
    if config.use_ai_ranking and config.openai_api_key:
        logger.info("Ranking links using AI...")
        links_to_crawl = rank_links(initial_links, base_url, config)
    else:
        links_to_crawl = initial_links
    
    # Limit to max_pages
    links_to_crawl = links_to_crawl[:config.max_pages]
    
    logger.info(f"Starting crawl of {len(links_to_crawl)} links")
    
    for i, link in enumerate(links_to_crawl, 1):
        url = link['url']
        
        # Skip if already visited
        if url in visited_urls:
            continue
        
        visited_urls.add(url)
        
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
                'content': markdown_content,
                'link_text': link.get('text', '')
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
            filename = f"{base_domain}_index.md"
        else:
            # Clean path and create filename
            clean_path = url_path.strip('/').replace('/', '_').replace('\\', '_')
            # Limit filename length
            if len(clean_path) > 100:
                clean_path = clean_path[:100]
            filename = f"{base_domain}_{clean_path}.md"
        
        filepath = config.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_data['title']}\n\n")
            f.write(f"Source: {page_data['url']}\n")
            if page_data.get('link_text'):
                f.write(f"Link Text: {page_data['link_text']}\n")
            f.write("\n---\n\n")
            f.write(page_data['content'])
        
        logger.debug(f"Saved: {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving page {page_data['url']}: {str(e)}", exc_info=True)

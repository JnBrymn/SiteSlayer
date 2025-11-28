"""
Homepage scraper - Extracts content and links from website homepage
"""

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from utils.fetch import fetch_page
from utils.logger import setup_logger
from scraper.link_rewriter import clean_and_filter_links
from scraper.markdown_converter import html_to_markdown
from scraper.crawler import save_page

logger = setup_logger(__name__)

def scrape_homepage(url, config):
    """
    Scrape the homepage and extract content and links
    
    Args:
        url (str): Homepage URL
        config (Config): Configuration object
        
    Returns:
        dict: Contains title, content, and links (links is list[str] of URLs)
    """
    try:
        # Fetch the page
        html_content = fetch_page(url, config)
        if not html_content:
            logger.error(f"Failed to fetch homepage: {url}")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract title
        title = soup.title.string if soup.title else urlparse(url).netloc
        logger.info(f"Page title: {title}")
        
        # Extract main content
        content = extract_main_content(soup)
        
        # Convert to markdown
        markdown_content = html_to_markdown(str(content), url)
        
        # Extract and clean links
        all_links = extract_links(soup, url)
        filtered_links = clean_and_filter_links(all_links, url, config)
        
        logger.info(f"Found {len(all_links)} total links, {len(filtered_links)} after filtering")
        
        # Save homepage content using save_page from crawler
        page_data = {
            'url': url,
            'title': title,
            'content': markdown_content
        }
        save_page(page_data, config)
        
        return {
            'url': url,
            'title': title,
            'content': markdown_content,
            'links': filtered_links
        }
        
    except Exception as e:
        logger.error(f"Error scraping homepage {url}: {str(e)}", exc_info=True)
        return None

def extract_main_content(soup):
    """Extract main content from the page, removing unnecessary elements"""
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
        element.decompose()
    
    # Try to find main content area
    main_content = (
        soup.find('main') or
        soup.find('article') or
        soup.find('div', {'id': 'content'}) or
        soup.find('div', {'class': ['content', 'main-content', 'post-content']}) or
        soup.find('body')
    )
    
    return main_content if main_content else soup

def extract_links(soup, base_url):
    """Extract all links from the page"""
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        # Skip empty, anchor-only, javascript, and mailto links
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue
        
        # Convert to absolute URL
        absolute_url = urljoin(base_url, href)
        
        links.append(absolute_url)
    
    return links

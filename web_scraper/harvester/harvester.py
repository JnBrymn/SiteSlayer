"""
HTML Harvester - Downloads complete HTML content using Playwright for JavaScript rendering
"""

from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import Error as PlaywrightError
from utils.logger import setup_logger
from config import USER_AGENT, sanitize_domain

logger = setup_logger(__name__)

def harvest_html(url, config):
    """
    Harvest complete HTML content using Playwright to render JavaScript
    
    Args:
        url (str): The URL to harvest
        config (Config): Configuration object
        
    Returns:
        str: Path to the saved index.html file, or None if failed
    """
    logger.info(f"Harvesting HTML content for: {url}")
    
    try:
        playwright = sync_playwright().start()
        
        try:
            # Launch browser
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            
            # Create context with user agent
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Create page and navigate
            page = context.new_page()
            
            logger.debug("Loading page with Playwright...")
            page.goto(url, wait_until='networkidle', timeout=getattr(config, 'timeout', 30) * 1000)
            
            # Get the rendered HTML
            html_content = page.content()
            logger.debug(f"Retrieved HTML content: {len(html_content)} characters")
            
            # Close browser resources
            page.close()
            context.close()
            browser.close()
            
        finally:
            playwright.stop()
        
        # Parse and rewrite URLs
        soup = BeautifulSoup(html_content, 'lxml')
        rewritten_html = rewrite_urls(soup, url)
        
        # Save to file
        domain = sanitize_domain(url)
        sites_dir = Path('sites')
        target_dir = sites_dir / domain
        target_dir.mkdir(parents=True, exist_ok=True)

        filepath = target_dir / 'index.html'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(rewritten_html))
        
        logger.info(f"Successfully saved HTML to: {filepath}")
        
        return str(filepath)
        
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout harvesting HTML for {url}: {str(e)}")
        return None
    except PlaywrightError as e:
        error_msg = str(e)
        if "Executable doesn't exist" in error_msg or "BrowserType.launch" in error_msg:
            logger.error(f"Playwright browser not installed. Please run: playwright install chromium")
            logger.error(f"Error details: {error_msg}")
        else:
            logger.error(f"Playwright error harvesting HTML for {url}: {error_msg}")
        return None
    except Exception as e:
        logger.error(f"Error harvesting HTML for {url}: {str(e)}", exc_info=True)
        return None

def rewrite_urls(soup, base_url):
    """
    Rewrite relative URLs in HTML to absolute URLs pointing to original website
    
    Args:
        soup (BeautifulSoup): Parsed HTML soup
        base_url (str): Base URL for making relative URLs absolute
        
    Returns:
        BeautifulSoup: Soup with rewritten URLs
    """
    logger.debug("Rewriting relative URLs to absolute")
    
    # Tags and attributes to rewrite
    tags_to_rewrite = {
        'img': ['src'],
        'script': ['src'],
        'link': ['href'],  # CSS, favicons, etc.
        'a': ['href'],     # Links
        'source': ['src'], # Audio/video sources
        'iframe': ['src'], # Embedded content
        'form': ['action'], # Form actions
    }
    
    for tag_name, attrs in tags_to_rewrite.items():
        for tag in soup.find_all(tag_name):
            for attr in attrs:
                if attr in tag.attrs:
                    href = tag[attr]
                    if href and not href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#')):
                        # It's relative, make absolute
                        absolute_url = urljoin(base_url, href)
                        tag[attr] = absolute_url
                        logger.debug(f"Rewrote {tag_name} {attr}: {href} -> {absolute_url}")
    
    # Also handle style attributes (CSS within HTML)
    for tag in soup.find_all(style=True):
        # Simple regex to find url() in styles
        import re
        style_content = tag['style']
        def repl_url(match):
            url_part = match.group(2)
            if not url_part.startswith(('http://', 'https://')):
                abs_url = urljoin(base_url, url_part)
                return match.group(1) + abs_url + match.group(3)
            return match.group(0)
        
        new_style = re.sub(r'(url\([\'"]?)([^\'"]+?)([\'"]?\))', repl_url, style_content)
        if new_style != style_content:
            tag['style'] = new_style
    
    return soup

"""
HTML Harvester - Downloads complete HTML content using Selenium for JavaScript rendering
"""

from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from utils.logger import setup_logger

logger = setup_logger(__name__)

def harvest_html(url, config):
    """
    Harvest complete HTML content using Selenium to render JavaScript
    
    Args:
        url (str): The URL to harvest
        config (Config): Configuration object
        
    Returns:
        str: Path to the saved index.html file, or None if failed
    """
    logger.info(f"Harvesting HTML content for: {url}")
    
    try:
        # Configure webdriver (try Chrome first, fallback to Firefox)
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.debug("Using Chrome webdriver with webdriver-manager")
        except Exception as e:
            logger.warning(f"Chrome not available, trying Firefox: {str(e)}")
            try:
                firefox_options = FirefoxOptions()
                firefox_options.add_argument('--headless')
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=firefox_options)
                logger.debug("Using Firefox webdriver with webdriver-manager")
            except Exception as e2:
                logger.error(f"Neither Chrome nor Firefox webdriver available: {str(e2)}")
                return None
        
        # Fetch page with Selenium (waits for JS)
        logger.debug("Loading page with Selenium...")
        driver.get(url)
        
        # Wait for page to load (basic wait)
        driver.implicitly_wait(10)
        
        # Get the rendered HTML
        html_content = driver.page_source
        logger.debug(f"Retrieved HTML content: {len(html_content)} characters")
        
        # Close browser
        driver.quit()
        
        # Parse and rewrite URLs
        soup = BeautifulSoup(html_content, 'lxml')
        rewritten_html = rewrite_urls(soup, url)
        
        # Save to file
        domain = config._sanitize_domain(url)
        sites_dir = Path('sites')
        target_dir = sites_dir / domain
        target_dir.mkdir(parents=True, exist_ok=True)

        filepath = target_dir / 'index.html'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(rewritten_html))
        
        logger.info(f"Successfully saved HTML to: {filepath}")
        
        return str(filepath)
        
    except Exception as e:
        logger.error(f"Error harvesting HTML for {url}: {str(e)}", exc_info=True)
        if driver:
            try:
                driver.quit()
            except:
                pass
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

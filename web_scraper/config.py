"""
Configuration management for SiteSlayer
"""

import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

# User Agent string for HTTP requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class Config:
    """Configuration settings for the web scraper"""
    
    def __init__(self, target_url):
        # Scraping Settings
        self.max_pages = 50
        self.timeout = 30
        self.delay_between_requests = 1.0
        self.max_concurrent_requests = 20
        
        # Output Settings - Use OS temporary directory
        temp_base = Path(tempfile.gettempdir())
        
        # Create a sanitized directory name from the domain
        domain = sanitize_domain(target_url)
        self.output_dir = temp_base / 'siteslayer' / domain

        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Link Filtering
        self.exclude_extensions = [
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
            '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg',
            '.mp4', '.avi', '.mov', '.mp3', '.wav'
        ]
        
        # Content Settings
        self.min_content_length = 100
        self.include_images = True
        
        # AI Settings
        self.use_ai_ranking = True
        self.ai_model = 'gpt-5-mini-2025-08-07'
        
        # JavaScript Rendering Settings
        self.use_js_rendering = False
        self.js_wait_time = 3

    
    def cleanup_temp_dir(self):
        """Remove the temporary output directory and all its contents"""
        try:
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                return True
        except Exception as e:
            # Log error but don't raise - cleanup failures shouldn't break the program
            return False
        return False

def sanitize_domain(url):
    """Sanitize a URL to create a safe directory name"""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    domain = domain.replace('.', '_').replace(':', '_').replace('/', '_')
    return domain
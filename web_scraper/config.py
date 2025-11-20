"""
Configuration management for SiteSlayer
"""

import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the web scraper"""
    
    def __init__(self, target_url=None):
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Scraping Settings
        self.max_pages = int(os.getenv('MAX_PAGES', '10'))
        self.timeout = int(os.getenv('TIMEOUT', '30'))
        self.delay_between_requests = float(os.getenv('DELAY_BETWEEN_REQUESTS', '1.0'))
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
        
        # User Agent
        self.user_agent = os.getenv(
            'USER_AGENT',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Output Settings - Create site-specific directory
        base_dir = Path(os.getenv('OUTPUT_DIR', 'websites'))
        
        if target_url:
            # Create a sanitized directory name from the domain
            domain = self._sanitize_domain(target_url)
            self.output_dir = base_dir / domain
        else:
            # Fallback for when no URL is provided
            self.output_dir = base_dir / 'default'
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Link Filtering
        self.exclude_extensions = [
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
            '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg',
            '.mp4', '.avi', '.mov', '.mp3', '.wav'
        ]
        
        # Content Settings
        self.min_content_length = int(os.getenv('MIN_CONTENT_LENGTH', '100'))
        self.include_images = os.getenv('INCLUDE_IMAGES', 'true').lower() == 'true'
        
        # AI Settings
        self.use_ai_ranking = os.getenv('USE_AI_RANKING', 'true').lower() == 'true'
        self.ai_model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        
        # JavaScript Rendering Settings
        self.use_js_rendering = os.getenv('USE_JS_RENDERING', 'false').lower() == 'true'
        self.js_wait_time = int(os.getenv('JS_WAIT_TIME', '3'))
    
    def _sanitize_domain(self, url):
        """Convert URL domain to a safe directory name"""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Replace dots and other special characters with underscores
        sanitized = domain.replace('.', '_').replace(':', '_').replace('/', '_')
        return sanitized
    
    def validate(self):
        """Validate configuration settings"""
        errors = []
        
        if self.use_ai_ranking and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when USE_AI_RANKING is enabled")
        
        if self.max_pages < 1:
            errors.append("MAX_PAGES must be at least 1")
        
        if self.timeout < 1:
            errors.append("TIMEOUT must be at least 1 second")
        
        return errors

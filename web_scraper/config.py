"""
Configuration management for SiteSlayer
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the web scraper"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Scraping Settings
        self.max_pages = int(os.getenv('MAX_PAGES', '50'))
        self.timeout = int(os.getenv('TIMEOUT', '30'))
        self.delay_between_requests = float(os.getenv('DELAY_BETWEEN_REQUESTS', '1.0'))
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
        
        # User Agent
        self.user_agent = os.getenv(
            'USER_AGENT',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Output Settings
        self.output_dir = Path(os.getenv('OUTPUT_DIR', 'web_scraper/output'))
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

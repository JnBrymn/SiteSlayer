#!/usr/bin/env python3
"""
Homepage Duplicator - Creates an exact copy of just the homepage
Preserves original styling and removes external links
"""

import os
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import hashlib
import time
from utils.logger import setup_logger

logger = setup_logger(__name__)

class HomepageDuplicator:
    def __init__(self, url, output_dir='web_scraper/homepage_local'):
        self.url = url
        self.domain = urlparse(url).netloc
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / 'assets'
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        (self.assets_dir / 'css').mkdir(parents=True, exist_ok=True)
        (self.assets_dir / 'js').mkdir(parents=True, exist_ok=True)
        (self.assets_dir / 'images').mkdir(parents=True, exist_ok=True)
        
        self.downloaded_assets = {}
        
    def download_asset(self, url, asset_type='images'):
        """Download an asset and return local path"""
        if not url or url.startswith(('data:', '#', 'javascript:', 'mailto:', 'tel:')):
            return url
        
        if url in self.downloaded_assets:
            return self.downloaded_assets[url]
        
        try:
            # Make URL absolute
            if url.startswith('//'):
                url = 'https:' + url
            elif not url.startswith('http'):
                url = urljoin(self.url, url)
            
            # Generate safe filename
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or 'index'
            
            if '.' not in filename:
                filename += '.tmp'
            
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{url_hash}{ext}"
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            local_path = self.assets_dir / asset_type / filename
            
            logger.info(f"  Downloading: {os.path.basename(url)}")
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            relative_path = f'assets/{asset_type}/{filename}'
            self.downloaded_assets[url] = relative_path
            
            time.sleep(0.2)
            return relative_path
            
        except Exception as e:
            logger.warning(f"    Failed: {str(e)}")
            return url
    
    def process_css(self, css_content, css_url):
        """Process CSS and download referenced assets"""
        def replace_url(match):
            url = match.group(1).strip('\'"')
            if url.startswith(('data:', '#')):
                return match.group(0)
            
            absolute_url = urljoin(css_url, url)
            local_path = self.download_asset(absolute_url, 'images')
            return f'url("{local_path}")'
        
        return re.sub(r'url\([\'"]?([^\)]+?)[\'"]?\)', replace_url, css_content)
    
    def duplicate_homepage(self):
        """Duplicate only the homepage with original styling"""
        logger.info("=" * 60)
        logger.info("SiteSlayer - Homepage Duplicator")
        logger.info(f"Creating exact copy of: {self.url}")
        logger.info("=" * 60)
        print()
        
        try:
            # Fetch homepage
            logger.info("Fetching homepage...")
            response = requests.get(self.url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print()
            
            # Download CSS
            logger.info("Downloading CSS stylesheets...")
            for link_tag in soup.find_all('link', rel='stylesheet'):
                if link_tag.get('href'):
                    css_url = urljoin(self.url, link_tag['href'])
                    local_css = self.download_asset(css_url, 'css')
                    
                    # Process CSS for embedded assets
                    if local_css.startswith('assets/'):
                        css_path = self.output_dir / local_css
                        if css_path.exists():
                            try:
                                with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    css_content = f.read()
                                processed = self.process_css(css_content, css_url)
                                with open(css_path, 'w', encoding='utf-8') as f:
                                    f.write(processed)
                            except Exception as e:
                                pass
                    
                    link_tag['href'] = local_css
            
            print()
            
            # Download JS
            logger.info("Downloading JavaScript files...")
            for script_tag in soup.find_all('script', src=True):
                js_url = urljoin(self.url, script_tag['src'])
                local_js = self.download_asset(js_url, 'js')
                script_tag['src'] = local_js
            
            print()
            
            # Download images
            logger.info("Downloading images...")
            for img_tag in soup.find_all('img'):
                # Handle src attribute
                if img_tag.get('src'):
                    img_url = urljoin(self.url, img_tag['src'])
                    local_img = self.download_asset(img_url, 'images')
                    img_tag['src'] = local_img
                
                # Handle srcset attribute
                if img_tag.get('srcset'):
                    srcset_parts = []
                    for srcset_item in img_tag['srcset'].split(','):
                        parts = srcset_item.strip().split()
                        if parts:
                            img_url = urljoin(self.url, parts[0])
                            local_img = self.download_asset(img_url, 'images')
                            parts[0] = local_img
                            srcset_parts.append(' '.join(parts))
                    img_tag['srcset'] = ', '.join(srcset_parts)
                
                # Handle data-src (lazy loading)
                if img_tag.get('data-src'):
                    img_url = urljoin(self.url, img_tag['data-src'])
                    local_img = self.download_asset(img_url, 'images')
                    img_tag['data-src'] = local_img
                    # Also set as src for immediate display
                    if not img_tag.get('src'):
                        img_tag['src'] = local_img
            
            # Handle picture tags with source elements
            for picture_tag in soup.find_all('picture'):
                for source_tag in picture_tag.find_all('source'):
                    if source_tag.get('srcset'):
                        srcset_parts = []
                        for srcset_item in source_tag['srcset'].split(','):
                            parts = srcset_item.strip().split()
                            if parts:
                                img_url = urljoin(self.url, parts[0])
                                local_img = self.download_asset(img_url, 'images')
                                parts[0] = local_img
                                srcset_parts.append(' '.join(parts))
                        source_tag['srcset'] = ', '.join(srcset_parts)
            
            # Download video sources
            logger.info("Downloading video files...")
            for video_tag in soup.find_all('video'):
                if video_tag.get('src'):
                    video_url = urljoin(self.url, video_tag['src'])
                    local_video = self.download_asset(video_url, 'images')
                    video_tag['src'] = local_video
                # Download sources in source tags
                for source_tag in video_tag.find_all('source'):
                    if source_tag.get('src'):
                        video_url = urljoin(self.url, source_tag['src'])
                        local_video = self.download_asset(video_url, 'images')
                        source_tag['src'] = local_video
            
            # Download audio sources
            logger.info("Downloading audio files...")
            for audio_tag in soup.find_all('audio'):
                if audio_tag.get('src'):
                    audio_url = urljoin(self.url, audio_tag['src'])
                    local_audio = self.download_asset(audio_url, 'images')
                    audio_tag['src'] = local_audio
                # Download sources in source tags
                for source_tag in audio_tag.find_all('source'):
                    if source_tag.get('src'):
                        audio_url = urljoin(self.url, source_tag['src'])
                        local_audio = self.download_asset(audio_url, 'images')
                        source_tag['src'] = local_audio
            
            # Process inline styles with background images
            for tag in soup.find_all(style=True):
                style = tag['style']
                if 'url(' in style:
                    def replace_url(match):
                        bg_url = match.group(1).strip('\'"')
                        absolute_url = urljoin(self.url, bg_url)
                        local_path = self.download_asset(absolute_url, 'images')
                        return f'url("{local_path}")'
                    
                    tag['style'] = re.sub(r'url\([\'"]?([^\)]+?)[\'"]?\)', replace_url, style)
            
            print()
            logger.info("Processing links...")
            
            # Handle links - remove external, disable internal
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Skip anchors
                if href.startswith('#'):
                    continue
                
                # Skip special links
                if href.startswith(('javascript:', 'mailto:', 'tel:')):
                    continue
                
                # Make absolute
                absolute_href = urljoin(self.url, href)
                parsed_href = urlparse(absolute_href)
                
                # Check if external
                if parsed_href.netloc and parsed_href.netloc != self.domain:
                    # Remove external link
                    a_tag['href'] = '#'
                    a_tag['onclick'] = 'return false;'
                    a_tag['title'] = 'External link removed in local copy'
                elif parsed_href.netloc == self.domain:
                    # Disable internal link
                    a_tag['href'] = '#'
                    a_tag['onclick'] = 'return false;'
                    a_tag['title'] = 'Link disabled in local copy'
            
            # Add subtle watermark at bottom
            watermark = soup.new_tag('div', style='position: fixed; bottom: 10px; right: 10px; background: rgba(255,255,255,0.9); padding: 5px 10px; border-radius: 4px; font-size: 10px; color: #999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);')
            watermark.string = 'Local Copy by SiteSlayer'
            body = soup.find('body')
            if body:
                body.append(watermark)
            
            # Save homepage
            output_path = self.output_dir / 'index.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print()
            logger.info("=" * 60)
            logger.info("✅ Homepage Duplication Complete!")
            logger.info("=" * 60)
            print()
            logger.info(f"📂 Location: {self.output_dir.absolute()}")
            logger.info(f"📦 Assets Downloaded: {len(self.downloaded_assets)}")
            logger.info(f"🌐 Open: {output_path.absolute()}")
            logger.info(f"🎨 Looks exactly like the original!")
            logger.info(f"🔒 External links removed for privacy")
            print()
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")


def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python web_scraper/homepage_duplicate.py <url>")
        print("Example: python web_scraper/homepage_duplicate.py https://www.example.com")
        return
    
    url = sys.argv[1]
    duplicator = HomepageDuplicator(url)
    duplicator.duplicate_homepage()


if __name__ == "__main__":
    main()

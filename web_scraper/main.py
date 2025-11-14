"""
SiteSlayer - Main Entry Point
Web scraper for extracting and converting website content to markdown
"""

import sys
import os
from pathlib import Path
from config import Config
from scraper.homepage import scrape_homepage
from scraper.crawler import crawl_site
from utils.logger import setup_logger

def main():
    """Main execution function"""
    logger = setup_logger(__name__)
    
    # Load configuration
    config = Config()
    
    # Get target URL from command line or config
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("Enter the website URL to scrape: ").strip()
    
    if not target_url:
        logger.error("No URL provided")
        return
    
    # Ensure URL has proper scheme
    if not target_url.startswith(('http://', 'https://')):
        target_url = f"https://{target_url}"
    
    logger.info(f"Starting to scrape: {target_url}")
    
    try:
        # Step 1: Scrape homepage
        logger.info("Step 1: Scraping homepage...")
        homepage_data = scrape_homepage(target_url, config)
        
        if not homepage_data:
            logger.error("Failed to scrape homepage")
            return
        
        logger.info(f"Homepage scraped successfully: {homepage_data['title']}")
        
        # Step 2: Crawl the site
        logger.info("Step 2: Crawling site for links...")
        crawl_results = crawl_site(target_url, homepage_data['links'], config)
        
        logger.info(f"Crawl complete. Total pages scraped: {len(crawl_results)}")
        
        # Display results summary
        print("\n" + "="*50)
        print("SCRAPING COMPLETE")
        print("="*50)
        print(f"Total pages scraped: {len(crawl_results)}")
        print(f"Output directory: {config.output_dir}")
        print("="*50 + "\n")
        
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

"""
SiteSlayer - Main Entry Point
Web scraper for extracting website HTML and markdown content
"""

import sys
import os
from pathlib import Path
from config import Config
from harvester import harvest_html
from scraper.homepage import scrape_homepage
from scraper.crawler import crawl_site
from scraper.markdown_aggregator import aggregate_markdown_content
from utils.logger import setup_logger
from urllib.parse import urlparse

def main():
    """Main execution function"""
    logger = setup_logger(__name__)

    # Get target URL from command line or config
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("Enter the website URL to harvest: ").strip()

    if not target_url:
        logger.error("No URL provided")
        return

    # Ensure URL has proper scheme
    if not target_url.startswith(('http://', 'https://')):
        target_url = f"https://{target_url}"

    # Load configuration with target URL
    config = Config(target_url)

    logger.info(f"Starting to harvest HTML: {target_url}")

    try:
        # Step 1: Harvest HTML from homepage
        logger.info("Step 1: Harvesting homepage HTML...")
        html_file = harvest_html(target_url, config)

        if html_file:
            logger.info(f"Homepage HTML harvested: {html_file}")
        else:
            logger.warning("HTML harvesting failed, continuing with markdown scraping")

        # Step 2: Scrape homepage for markdown
        logger.info("Step 2: Scraping homepage...")
        homepage_data = scrape_homepage(target_url, config)

        if not homepage_data:
            logger.error("Failed to scrape homepage")
            return

        logger.info(f"Homepage scraped successfully: {homepage_data['title']}")

        # Step 3: Crawl the site
        logger.info("Step 3: Crawling site for links...")
        crawl_results = crawl_site(target_url, homepage_data['links'], config)

        logger.info(f"Crawl complete. Total pages scraped: {len(crawl_results)}")

        # Step 4: Aggregate markdown content for chatbot
        logger.info("Step 4: Aggregating markdown content...")
        domain = config._sanitize_domain(target_url)
        content_file = aggregate_markdown_content(domain)

        # Display results summary
        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)
        print(f"HTML file: {html_file or 'N/A'}")
        print(f"Total pages scraped: {len(crawl_results)}")
        print(f"Output directory: {config.output_dir}")
        if content_file:
            print(f"Aggregated content: {content_file}")
        print("="*50 + "\n")

    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

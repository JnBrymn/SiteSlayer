"""
Standalone utility to aggregate markdown content for existing scraped sites
"""

import sys
from pathlib import Path
from scraper.markdown_aggregator import aggregate_markdown_content
from utils.logger import setup_logger

def main():
    """Main execution function for standalone aggregator"""
    logger = setup_logger(__name__)
    
    print("="*60)
    print("SiteSlayer - Markdown Content Aggregator")
    print("="*60)
    print()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        domain = sys.argv[1]
        process_single_domain(domain, logger)
    else:
        # Interactive mode - show available domains
        websites_dir = Path('websites')
        
        if not websites_dir.exists():
            logger.error("No 'websites' directory found")
            return
        
        # Get all domain directories
        domains = [d.name for d in websites_dir.iterdir() if d.is_dir()]
        
        if not domains:
            logger.error("No scraped websites found in 'websites' directory")
            return
        
        print(f"Found {len(domains)} scraped website(s):\n")
        for i, domain in enumerate(domains, 1):
            print(f"  {i}. {domain}")
        
        print(f"\n  {len(domains) + 1}. Process ALL sites")
        print("  0. Exit")
        print()
        
        try:
            choice = input("Select an option: ").strip()
            
            if choice == '0':
                print("Exiting...")
                return
            
            choice_num = int(choice)
            
            if choice_num == len(domains) + 1:
                # Process all sites
                process_all_domains(domains, logger)
            elif 1 <= choice_num <= len(domains):
                # Process selected site
                selected_domain = domains[choice_num - 1]
                process_single_domain(selected_domain, logger)
            else:
                logger.error("Invalid selection")
                
        except ValueError:
            logger.error("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")


def process_single_domain(domain, logger):
    """Process a single domain"""
    print()
    logger.info(f"Processing domain: {domain}")
    print("-" * 60)
    
    content_file = aggregate_markdown_content(domain)
    
    if content_file:
        print()
        print("="*60)
        print("SUCCESS")
        print("="*60)
        print(f"Created: {content_file}")
        print("="*60)
    else:
        print()
        print("="*60)
        print("FAILED")
        print("="*60)
        print(f"Could not aggregate content for: {domain}")
        print("="*60)


def process_all_domains(domains, logger):
    """Process all domains"""
    print()
    logger.info(f"Processing all {len(domains)} domains...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    for domain in domains:
        print(f"\nProcessing: {domain}")
        content_file = aggregate_markdown_content(domain)
        
        if content_file:
            successful += 1
            print(f"  ✓ Success: {content_file}")
        else:
            failed += 1
            print(f"  ✗ Failed: {domain}")
    
    print()
    print("="*60)
    print("BATCH PROCESSING COMPLETE")
    print("="*60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(domains)}")
    print("="*60)


if __name__ == "__main__":
    main()

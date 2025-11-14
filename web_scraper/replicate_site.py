"""
Replicate Site - Converts scraped markdown to HTML pages
"""

import sys
from pathlib import Path
from generator.html_generator import generate_html_from_markdown, generate_index_page
from utils.logger import setup_logger

logger = setup_logger(__name__)

def replicate_site(output_dir='web_scraper/output'):
    """
    Convert all scraped markdown files to HTML
    
    Args:
        output_dir (str): Directory containing markdown files
    """
    output_path = Path(output_dir)
    
    if not output_path.exists():
        logger.error(f"Output directory not found: {output_dir}")
        logger.info("Please run the scraper first: python web_scraper/main.py <url>")
        return
    
    # Find all markdown files
    md_files = list(output_path.glob('*.md'))
    
    if not md_files:
        logger.error(f"No markdown files found in {output_dir}")
        logger.info("Please run the scraper first to generate markdown files")
        return
    
    logger.info(f"Found {len(md_files)} markdown files to convert")
    
    # Convert each markdown file to HTML
    converted = 0
    for md_file in md_files:
        try:
            html_file = md_file.with_suffix('.html')
            logger.info(f"Converting: {md_file.name} -> {html_file.name}")
            
            generate_html_from_markdown(
                markdown_file=str(md_file),
                output_html=str(html_file)
            )
            converted += 1
            
        except Exception as e:
            logger.error(f"Failed to convert {md_file.name}: {str(e)}")
    
    # Generate index page
    logger.info("Generating index page...")
    generate_index_page(output_path, title="Scraped Website")
    
    # Summary
    print("\n" + "="*50)
    print("HTML GENERATION COMPLETE")
    print("="*50)
    print(f"Converted: {converted}/{len(md_files)} files")
    print(f"Output directory: {output_path.absolute()}")
    print(f"\nOpen the site:")
    print(f"  {output_path.absolute() / 'index.html'}")
    print("="*50 + "\n")

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = 'web_scraper/output'
    
    replicate_site(output_dir)

if __name__ == "__main__":
    main()

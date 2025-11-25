"""
Markdown Aggregator - Combines all scraped markdown files into a single content.md file
for AI chatbot consumption
"""

import os
from pathlib import Path
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

def aggregate_markdown_content(domain, temp_dir=None, sites_dir='sites'):
    """
    Aggregate all markdown files from a scraped website into a single content.md file
    
    Args:
        domain (str): The domain name (sanitized) of the website
        temp_dir (Path): Path to temporary directory containing individual markdown files
        sites_dir (str): Directory where content.md will be saved
        
    Returns:
        str: Path to the created content.md file, or None if failed
    """
    logger.info(f"Aggregating markdown content for: {domain}")
    
    # Define paths
    if temp_dir is None:
        # Fallback to old behavior for backwards compatibility
        source_dir = Path('websites') / domain
    else:
        source_dir = Path(temp_dir)
    
    target_dir = Path(sites_dir) / domain
    
    # Validate source directory exists
    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        return None
    
    # Get all markdown files
    md_files = list(source_dir.glob('*.md'))
    
    if not md_files:
        logger.warning(f"No markdown files found in: {source_dir}")
        return None
    
    logger.info(f"Found {len(md_files)} markdown files to aggregate")
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare aggregated content
    aggregated_content = []
    
    # Add header
    aggregated_content.append(f"# Website Content: {domain}")
    aggregated_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    aggregated_content.append(f"Total Pages: {len(md_files)}")
    aggregated_content.append("\n---\n")
    
    # Process each markdown file
    successful_files = 0
    for md_file in sorted(md_files):
        try:
            logger.debug(f"Processing: {md_file.name}")
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from the file
            metadata = extract_metadata(content)
            
            # Add page section
            aggregated_content.append(f"\n## PAGE: {metadata['title']}")
            aggregated_content.append(f"**Source URL:** {metadata['url']}")
            
            if metadata['link_text']:
                aggregated_content.append(f"**Link Text:** {metadata['link_text']}")
            
            aggregated_content.append(f"**File:** {md_file.name}")
            aggregated_content.append("")  # Empty line
            
            # Add the actual content (skip the metadata section)
            page_content = extract_page_content(content)
            aggregated_content.append(page_content)
            
            aggregated_content.append("\n---\n")
            
            successful_files += 1
            
        except Exception as e:
            logger.error(f"Error processing {md_file.name}: {str(e)}", exc_info=True)
            continue
    
    if successful_files == 0:
        logger.error("Failed to process any markdown files")
        return None
    
    # Write aggregated content to file
    output_file = target_dir / 'content.md'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(aggregated_content))
        
        logger.info(f"Successfully created content.md at: {output_file}")
        logger.info(f"Aggregated {successful_files} pages")

        return str(output_file)
        
    except Exception as e:
        logger.error(f"Error writing content.md: {str(e)}", exc_info=True)
        return None


def extract_metadata(content):
    """
    Extract metadata from markdown file
    
    Args:
        content (str): The markdown file content
        
    Returns:
        dict: Dictionary containing title, url, and link_text
    """
    metadata = {
        'title': 'Untitled',
        'url': '',
        'link_text': ''
    }
    
    lines = content.split('\n')
    
    for line in lines[:10]:  # Check first 10 lines for metadata
        line = line.strip()
        
        # Extract title (first heading)
        if line.startswith('# ') and metadata['title'] == 'Untitled':
            metadata['title'] = line[2:].strip()
        
        # Extract source URL
        elif line.startswith('Source:'):
            metadata['url'] = line.replace('Source:', '').strip()
        
        # Extract link text
        elif line.startswith('Link Text:'):
            metadata['link_text'] = line.replace('Link Text:', '').strip()
    
    return metadata


def extract_page_content(content):
    """
    Extract the main page content, skipping the metadata header section
    
    Args:
        content (str): The full markdown file content
        
    Returns:
        str: The page content without metadata
    """
    lines = content.split('\n')
    
    # Find the separator (---) that marks end of metadata
    separator_index = -1
    for i, line in enumerate(lines):
        if line.strip() == '---':
            separator_index = i
            break
    
    # If separator found, return content after it
    if separator_index >= 0 and separator_index < len(lines) - 1:
        return '\n'.join(lines[separator_index + 1:]).strip()
    
    # Otherwise return content after the first few metadata lines
    # Skip first heading, source, link text, and empty line
    content_start = 0
    for i, line in enumerate(lines[:10]):
        if line.strip() == '' and content_start == 0:
            content_start = i + 1
            break
    
    return '\n'.join(lines[content_start:]).strip()

"""
HTML to Markdown conversion utilities
"""

from markdownify import markdownify as md
from utils.logger import setup_logger

logger = setup_logger(__name__)

def html_to_markdown(html_content, base_url=None):
    """
    Convert HTML content to Markdown
    
    Args:
        html_content (str): HTML content to convert
        base_url (str, optional): Base URL for resolving relative links
        
    Returns:
        str: Markdown formatted content
    """
    try:
        # Convert HTML to Markdown
        markdown = md(
            html_content,
            heading_style="ATX",  # Use # style headings
            bullets="-",  # Use - for bullet lists
            strip=['script', 'style'],  # Remove script and style tags
            escape_asterisks=False,
            escape_underscores=False,
        )
        
        return markdown
        
    except Exception as e:
        logger.error(f"Error converting HTML to Markdown: {str(e)}", exc_info=True)
        return ""

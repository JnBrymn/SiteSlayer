"""
AI-powered link ranking using OpenAI
"""

import os
from pydantic import BaseModel
from openai import OpenAI
from utils.logger import setup_logger
from scraper.link_rewriter import clean_and_filter_links

PREVIEW_LENGTH = 100000  # Length of content preview to send to AI

logger = setup_logger(__name__)

class URLList(BaseModel):
    """Pydantic model for list of URLs"""
    urls: list[str]

def rank_links(content: str, target_url: str, config):
    """
    Extract relevant URLs using AI based on homepage content
    
    Args:
        content (str): The homepage content (markdown text)
        target_url (str): The target URL of the site
        config (Config): Configuration object
        
    Returns:
        list[str]: List of relevant URLs
        
    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
    """
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        error_msg = "OPENAI_API_KEY environment variable is required for AI ranking but was not found"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        client = OpenAI()
        
        # Truncate content if too long
        content_preview = content[:PREVIEW_LENGTH] if len(content) > PREVIEW_LENGTH else content
        
        prompt = f"""Return a list of URLs that seem most relevant to understanding {target_url} based on this text:

{content_preview}

- Only include URLs that are mentioned in the text.
- Only return URLs that contain html or text content of some sort (e.g. no images, raw data, or complex document types like pdfs or word documents).
- Don't return urls with fragments like https://example.com#fragment.
- Return only unique content - for example https://www.hello.com/index.html and https://www.hello.com are the same.
- Don't return {target_url}.

Return a list of full URL strings."""

        completion = client.chat.completions.parse(
            model=config.ai_model,
            messages=[
                {"role": "system", "content": "You are a web content analysis assistant. Extract relevant URLs from the content."},
                {"role": "user", "content": prompt}
            ],
            response_format=URLList
        )
        
        # Get parsed response - extract the list[str] from the model
        parsed_response = completion.choices[0].message.parsed
        urls = parsed_response.urls if parsed_response else []
        
        # Filter URLs using the same logic as scrape_homepage
        filtered_urls = clean_and_filter_links(urls, target_url, config)
        
        logger.info(f"AI extracted {len(urls)} URLs, {len(filtered_urls)} after filtering")
        return filtered_urls
        
    except Exception as e:
        logger.error(f"Error ranking links with AI: {str(e)}", exc_info=True)
        logger.info("Falling back to empty list")
        return []

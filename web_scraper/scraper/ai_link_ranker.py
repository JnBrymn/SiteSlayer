"""
AI-powered link ranking using OpenAI
"""

import json
from openai import OpenAI
from utils.logger import setup_logger

logger = setup_logger(__name__)

def rank_links(links, base_url, config):
    """
    Rank links using AI based on their relevance and importance
    
    Args:
        links (list): List of link dictionaries
        base_url (str): Base URL of the site
        config (Config): Configuration object
        
    Returns:
        list: Ranked list of links
    """
    if not config.openai_api_key:
        logger.warning("No OpenAI API key provided, skipping AI ranking")
        return links
    
    try:
        client = OpenAI(api_key=config.openai_api_key)
        
        # Prepare prompt
        links_text = "\n".join([
            f"{i+1}. URL: {link['url']}, Text: {link['text']}"
            for i, link in enumerate(links[:100])  # Limit to first 100 for API
        ])
        
        prompt = f"""You are helping to prioritize web pages for scraping from the website: {base_url}

Below is a list of links found on the homepage. Please rank them by importance and relevance for understanding the website's main content. Prioritize:
1. Documentation, guides, and informational pages
2. Product/service pages
3. About and company information pages
4. Blog posts and articles
5. Avoid: Login pages, external links, social media, contact forms

Links:
{links_text}

Respond with a JSON array of numbers representing the ranking (1 being most important). For example: [3, 1, 5, 2, 4, ...]
Only include the JSON array, no other text."""

        response = client.chat.completions.create(
            model=config.ai_model,
            messages=[
                {"role": "system", "content": "You are a web content analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse response
        ranking_text = response.choices[0].message.content.strip()
        
        # Extract JSON array from response
        if '[' in ranking_text and ']' in ranking_text:
            start = ranking_text.index('[')
            end = ranking_text.rindex(']') + 1
            ranking_text = ranking_text[start:end]
        
        ranking = json.loads(ranking_text)
        
        # Create ranked list
        ranked_links = []
        for rank_idx in ranking:
            if 0 < rank_idx <= len(links):
                ranked_links.append(links[rank_idx - 1])
        
        # Add any links not in the ranking
        ranked_urls = {link['url'] for link in ranked_links}
        for link in links:
            if link['url'] not in ranked_urls:
                ranked_links.append(link)
        
        logger.info(f"Successfully ranked {len(ranked_links)} links using AI")
        return ranked_links
        
    except Exception as e:
        logger.error(f"Error ranking links with AI: {str(e)}", exc_info=True)
        logger.info("Falling back to original link order")
        return links

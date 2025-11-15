"""
Analyze scraped markdown files to identify the most important links
for understanding website content using AI
"""

import sys
import re
from pathlib import Path
from openai import OpenAI
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def extract_links_from_markdown(markdown_content):
    """
    Extract all links from markdown content
    
    Args:
        markdown_content (str): Markdown text
        
    Returns:
        list: List of dictionaries with link info
    """
    links = []
    
    # Pattern for markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    
    for match in re.finditer(link_pattern, markdown_content):
        link_text = match.group(1)
        url = match.group(2)
        
        # Get context around the link (50 chars before and after)
        start = max(0, match.start() - 50)
        end = min(len(markdown_content), match.end() + 50)
        context = markdown_content[start:end].replace('\n', ' ')
        
        links.append({
            'text': link_text,
            'url': url,
            'context': context
        })
    
    return links

def analyze_links_with_ai(website_dir, config):
    """
    Analyze all links from markdown files using AI
    
    Args:
        website_dir (Path): Directory containing markdown files
        config (Config): Configuration object
        
    Returns:
        dict: Analysis results
    """
    if not config.openai_api_key:
        logger.error("No OpenAI API key provided. Please set OPENAI_API_KEY in your .env file")
        return None
    
    # Find all markdown files
    md_files = list(website_dir.glob('*.md'))
    
    if not md_files:
        logger.error(f"No markdown files found in {website_dir}")
        return None
    
    logger.info(f"Found {len(md_files)} markdown files to analyze")
    
    # Extract all links from all files
    all_links = []
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                links = extract_links_from_markdown(content)
                
                # Add source file info
                for link in links:
                    link['source_file'] = md_file.name
                
                all_links.extend(links)
        except Exception as e:
            logger.error(f"Error reading {md_file}: {str(e)}")
    
    if not all_links:
        logger.warning("No links found in markdown files")
        return None
    
    logger.info(f"Extracted {len(all_links)} total links")
    
    # Prepare data for AI
    # Group links by URL to avoid duplicates
    unique_links = {}
    for link in all_links:
        url = link['url']
        if url not in unique_links:
            unique_links[url] = link
        # If we see the same URL multiple times, it might be more important
        else:
            if 'frequency' not in unique_links[url]:
                unique_links[url]['frequency'] = 1
            unique_links[url]['frequency'] += 1
    
    # Convert to list
    links_list = list(unique_links.values())
    
    # Limit to 50 most frequent links for API efficiency
    links_list.sort(key=lambda x: x.get('frequency', 1), reverse=True)
    links_to_analyze = links_list[:50]
    
    # Create prompt
    website_name = website_dir.name.replace('_', '.')
    
    links_text = ""
    for i, link in enumerate(links_to_analyze, 1):
        freq = link.get('frequency', 1)
        freq_text = f" (appears {freq}x)" if freq > 1 else ""
        links_text += f"{i}. [{link['text']}]({link['url']}){freq_text}\n"
        links_text += f"   Context: ...{link['context']}...\n\n"
    
    prompt = f"""You are analyzing a scraped website: {website_name}

I have extracted {len(links_list)} unique links from the markdown files. Below are the most frequent/prominent links.

Please identify the TOP 10 most important links that would help someone understand:
1. What this website is about
2. Its main content and purpose
3. Key sections or features

Consider:
- Links that appear multiple times are likely more important
- Core navigation links (About, Products, Services, etc.)
- Main content categories
- Avoid: Individual product pages, external social media links, login/account pages

Links to analyze:
{links_text}

Respond with a JSON array of objects, each with:
- "rank": 1-10
- "url": the URL
- "text": the link text
- "reason": brief explanation why this link is important

Example format:
[
  {{"rank": 1, "url": "/about", "text": "About Us", "reason": "Core information about the company"}},
  {{"rank": 2, "url": "/products", "text": "Products", "reason": "Main product catalog"}}
]

Only return the JSON array, no other text."""

    try:
        client = OpenAI(api_key=config.openai_api_key)
        
        logger.info("Sending request to AI for link analysis...")
        
        response = client.chat.completions.create(
            model=config.ai_model,
            messages=[
                {"role": "system", "content": "You are a web content analysis expert who identifies the most important links for understanding a website's purpose and content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        import json
        if '[' in response_text and ']' in response_text:
            start = response_text.index('[')
            end = response_text.rindex(']') + 1
            response_text = response_text[start:end]
        
        important_links = json.loads(response_text)
        
        logger.info(f"Successfully analyzed links with AI")
        
        return {
            'website': website_name,
            'total_links': len(links_list),
            'analyzed_links': len(links_to_analyze),
            'important_links': important_links
        }
        
    except Exception as e:
        logger.error(f"Error analyzing links with AI: {str(e)}", exc_info=True)
        return None

def print_results(results):
    """Print analysis results in a formatted way"""
    if not results:
        return
    
    print("\n" + "="*70)
    print(f"LINK ANALYSIS RESULTS FOR: {results['website']}")
    print("="*70)
    print(f"Total unique links found: {results['total_links']}")
    print(f"Links analyzed by AI: {results['analyzed_links']}")
    print("\n" + "="*70)
    print("TOP 10 MOST IMPORTANT LINKS:")
    print("="*70 + "\n")
    
    for link in results['important_links']:
        print(f"#{link['rank']}: {link['text']}")
        print(f"   URL: {link['url']}")
        print(f"   Why: {link['reason']}")
        print()
    
    print("="*70 + "\n")

def main():
    """Main execution function"""
    logger = setup_logger(__name__)
    
    # Get directory from command line
    if len(sys.argv) < 2:
        print("Usage: python web_scraper/analyze_links.py <website_directory>")
        print("Example: python web_scraper/analyze_links.py websites/www_tcgplayer_com")
        return
    
    website_dir = Path(sys.argv[1])
    
    if not website_dir.exists():
        logger.error(f"Directory not found: {website_dir}")
        return
    
    if not website_dir.is_dir():
        logger.error(f"Not a directory: {website_dir}")
        return
    
    # Load configuration
    config = Config()
    
    # Analyze links
    logger.info(f"Analyzing links from: {website_dir}")
    results = analyze_links_with_ai(website_dir, config)
    
    if results:
        print_results(results)
        
        # Optionally save to file
        output_file = website_dir / "link_analysis.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to: {output_file}")
    else:
        logger.error("Link analysis failed")

if __name__ == "__main__":
    main()

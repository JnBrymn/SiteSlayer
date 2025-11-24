"""
Test script for markdown aggregator
"""

from web_scraper.scraper.markdown_aggregator import aggregate_markdown_content

# Test with an existing site
print("Testing markdown aggregator...")
print("="*60)

# Test with www_example_com
result = aggregate_markdown_content('www_example_com')

if result:
    print(f"\nSuccess! Created: {result}")
    
    # Read and display a preview of the content
    with open(result, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n" + "="*60)
    print("PREVIEW OF GENERATED CONTENT:")
    print("="*60)
    print(content[:1000])  # Show first 1000 characters
    print("\n... (content truncated)")
    print("="*60)
else:
    print("Failed to create aggregated content")

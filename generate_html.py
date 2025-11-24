#!/usr/bin/env python3
"""
Generate HTML from markdown for www_bigthunderevents_com
"""

from pathlib import Path
from web_scraper.generator.html_generator import generate_html_from_markdown

# Paths
content_md = Path("sites/www_bigthunderevents_com/content.md")
output_html = Path("sites/www_bigthunderevents_com/index.html")

print(f"Generating HTML from {content_md}")
print(f"Output will be saved to {output_html}")

# Generate the HTML
result = generate_html_from_markdown(
    markdown_file=str(content_md),
    output_html=str(output_html),
    title="Big Thunder Events - Nashville Party Rentals"
)

if result:
    print(f"\n✅ Success! HTML file created at {output_html}")
else:
    print("\n❌ Failed to generate HTML")

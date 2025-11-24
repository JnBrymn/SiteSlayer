# Automatic HTML Generation

## Overview

The SiteSlayer scraper now **automatically generates HTML files** whenever you aggregate markdown content for a scraped website. This means you'll always have both a `content.md` file (for AI/text processing) and an `index.html` file (for viewing in a browser) in the `sites/` directory.

## How It Works

### Automatic Generation Process

When you run the content aggregation:

```bash
python web_scraper/aggregate_content.py
```

The system will:

1. ✅ Aggregate all markdown files into `sites/{domain}/content.md`
2. ✅ **Automatically generate** `sites/{domain}/index.html`
3. ✅ Parse and format the content with proper styling
4. ✅ Create a table of contents with page links
5. ✅ Add appropriate emoji icons for each page type

### What Gets Generated

For each scraped website, you'll get:

```
sites/
└── www_bigthunderevents_com/
    ├── content.md          # Aggregated markdown content
    └── index.html          # Beautiful HTML webpage (AUTOMATICALLY CREATED!)
```

### HTML Features

The automatically generated HTML includes:

- **Modern Design**: Gradient header, clean layout, responsive
- **Table of Contents**: Easy navigation to all pages
- **Page Sections**: Each scraped page in its own section
- **Smart Icons**: Automatic emoji icons based on content type
  - 🏰 Bounce houses
  - 💦 Water slides
  - 🎮 Interactive games
  - 🎡 Mechanical rides
  - 🏃 Obstacle courses
  - 🏠 Homepage
  - And more!
- **Source Links**: Direct links back to original URLs
- **Images**: All images from original content displayed
- **Formatted Content**: Proper headers, paragraphs, links

## Viewing the HTML

Simply open the generated `index.html` file in your browser:

**Windows:**

```bash
start sites/www_bigthunderevents_com/index.html
```

**Mac:**

```bash
open sites/www_bigthunderevents_com/index.html
```

**Linux:**

```bash
xdg-open sites/www_bigthunderevents_com/index.html
```

Or just double-click the file in your file explorer!

## When HTML is Generated

HTML is automatically created/updated when you:

1. **Run aggregate_content.py** - Processes websites/ directory content
2. **Complete a scraping session** - If your scraper calls the aggregation function

## Technical Details

### Code Location

The HTML generation is handled in:

- `web_scraper/scraper/markdown_aggregator.py`
- Function: `generate_html_from_content()`

### Customization

To customize the HTML appearance, edit the `generate_html_template()` function in `markdown_aggregator.py`:

- **Styling**: Modify the `<style>` section for colors, fonts, layout
- **Icons**: Update `get_page_icon()` function for different emoji mappings
- **Structure**: Change the HTML template structure as needed

## Benefits

### Before (Manual Process)

1. ❌ Scrape website → markdown files
2. ❌ Run aggregation → content.md created
3. ❌ Manually create HTML (tedious!)
4. ❌ Or use separate tool to view content

### Now (Automatic Process)

1. ✅ Scrape website → markdown files
2. ✅ Run aggregation → **BOTH** content.md **AND** index.html created!
3. ✅ Open in browser immediately!
4. ✅ No extra steps needed!

## Example Output

For `www_bigthunderevents_com`, the HTML shows:

- Clean header: "🌐 www_bigthunderevents_com"
- Metadata: Generation time and page count
- Table of contents with 6 pages
- All page content beautifully formatted
- Footer with attribution

## Troubleshooting

### HTML not generating?

1. Check logs for errors during aggregation
2. Ensure content.md was created successfully
3. Verify Python has write permissions to sites/ directory

### HTML looks wrong?

1. The markdown parsing is basic but handles most content
2. For complex formatting, the content.md is still the source of truth
3. Custom HTML/CSS in markdown may not render perfectly

### Want to regenerate HTML only?

Currently, HTML regenerates whenever you run aggregation. If you need to regenerate without re-aggregating:

```python
from web_scraper.scraper.markdown_aggregator import generate_html_from_content

# Regenerate HTML for a specific site
generate_html_from_content(
    'sites/www_bigthunderevents_com/content.md',
    'www_bigthunderevents_com',
    6  # number of pages
)
```

## Future Enhancements

Possible improvements:

- [ ] Dark mode toggle
- [ ] Search functionality
- [ ] Export to PDF
- [ ] Custom CSS themes
- [ ] Interactive JavaScript features

---

**Note**: This feature was added to ensure every scraped website automatically has a viewable HTML version alongside the markdown content, making it easier to browse and verify scraped content without additional tools.

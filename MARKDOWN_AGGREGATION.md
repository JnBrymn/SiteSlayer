# Markdown Aggregation Feature

## Overview

The markdown aggregation system automatically combines all scraped markdown files from a website into a single `content.md` file, optimized for AI chatbot consumption.

## Directory Structure

```
websites/            # Individual markdown files from web scraping
├── <domain>/
│   ├── homepage.md
│   ├── about.md
│   └── ...

sites/               # Aggregated content for AI chatbots
├── <domain>/
│   └── content.md   # Combined content file
```

## Features

- **Automatic aggregation** after web scraping completes
- **Metadata preservation** - includes page titles, URLs, and link text
- **Structured format** - clear separators between pages for easy parsing
- **Standalone utility** - for processing existing scraped sites
- **Batch processing** - aggregate multiple sites at once

## Content Format

The aggregated `content.md` file follows this structure:

```markdown
# Website Content: <domain>

Generated: <timestamp>
Total Pages: <count>

---

## PAGE: <Page Title>

**Source URL:** <url>
**Link Text:** <link_text>
**File:** <filename>

<page content here>

---

## PAGE: <Next Page Title>

...
```

## Usage

### Automatic Aggregation

When you run the main scraper, aggregation happens automatically:

```bash
python web_scraper/main.py https://example.com
```

The scraper will:

1. Scrape all pages and save to `websites/<domain>/`
2. Automatically aggregate into `sites/<domain>/content.md`

### Manual Aggregation

Use the standalone utility to process existing sites:

```bash
# Process a specific site
python web_scraper/aggregate_content.py www_example_com

# Interactive mode - select from available sites
python web_scraper/aggregate_content.py
```

### Batch Processing

In interactive mode, you can choose to process all sites:

```bash
python web_scraper/aggregate_content.py
# Select "Process ALL sites" option
```

## AI Chatbot Integration

The aggregated `content.md` file is optimized for AI chatbots:

### Benefits

1. **Single file** - Easy to load into chatbot context
2. **Metadata rich** - Each page section includes source URL and title
3. **Structured** - Clear page boundaries with `---` separators
4. **Complete content** - All website information in one place

### Example Integration

```python
# Example: Loading content for a chatbot
with open('sites/www_example_com/content.md', 'r') as f:
    website_content = f.read()

# Use this content as context for your AI chatbot
# The chatbot can now answer questions about the website
```

### Chatbot Prompt Example

```
You are a helpful assistant with access to information about <website>.
Here is the complete content from the website:

<load content.md here>

Answer user questions based on this information.
```

## Technical Details

### Module: `web_scraper/scraper/markdown_aggregator.py`

Core functions:

- `aggregate_markdown_content(domain)` - Main aggregation function
- `extract_metadata(content)` - Extract page metadata
- `extract_page_content(content)` - Clean page content

### Integration: `web_scraper/main.py`

After crawling completes, the aggregator runs automatically:

```python
# Step 3: Aggregate markdown content for chatbot
logger.info("Step 3: Aggregating markdown content...")
domain = config._sanitize_domain(target_url)
content_file = aggregate_markdown_content(domain)
```

### Standalone Utility: `web_scraper/aggregate_content.py`

Provides a CLI interface for:

- Processing specific domains
- Interactive selection from available sites
- Batch processing all sites

## Error Handling

The aggregator includes robust error handling:

- Validates source directory exists
- Skips corrupted markdown files
- Logs processing status for each file
- Continues processing even if individual files fail

## Examples

### Example 1: Simple Site

```markdown
# Website Content: www_example_com

Generated: 2025-11-19 23:08:35
Total Pages: 1

---

## PAGE: Example Domain

**Source URL:** https://www.example.com
**File:** homepage.md

This domain is for use in documentation examples...
```

### Example 2: Multi-Page Site

```markdown
# Website Content: www_python_org

Generated: 2025-11-19 23:09:15
Total Pages: 14

---

## PAGE: Welcome to Python.org

**Source URL:** https://www.python.org
**File:** homepage.md

Python is a programming language...

---

## PAGE: Getting Started

**Source URL:** https://www.python.org/about/gettingstarted/
**Link Text:** Start with our Beginner's Guide
**File:** about_gettingstarted.md

Welcome! Are you completely new to programming?...
```

## Troubleshooting

### No markdown files found

**Problem:** `No markdown files found in: websites/<domain>`

**Solution:** Ensure you've scraped the site first using `web_scraper/main.py`

### Permission errors

**Problem:** Cannot create `sites/<domain>/` directory

**Solution:** Check write permissions in the project directory

### Encoding issues

**Problem:** Special characters not displaying correctly

**Solution:** The aggregator uses UTF-8 encoding by default. Ensure your editor supports UTF-8.

## Future Enhancements

Potential improvements:

- [ ] Custom output formats (JSON, XML)
- [ ] Filtering options (exclude certain pages)
- [ ] Search index generation
- [ ] Table of contents generation
- [ ] Chunking for large sites (to fit in AI context windows)

# SiteSlayer

A powerful web scraper that extracts content from websites and converts it into clean, readable Markdown format. Features AI-powered link ranking and intelligent content extraction.

## Features

- 🚀 **Easy to Use**: Simple command-line interface
- 📝 **Markdown Conversion**: Converts HTML to clean, formatted Markdown
- 🤖 **AI-Powered Link Ranking**: Uses OpenAI to intelligently prioritize important pages
- 🎯 **Smart Content Extraction**: Focuses on main content, filters out navigation and boilerplate
- ⚙️ **Configurable**: Extensive configuration options via environment variables
- 📊 **Progress Tracking**: Colored console output with detailed logging
- 🔄 **Automatic Filtering**: Removes duplicate links and unwanted file types
- 🤝 **AI Chatbot Ready**: Automatically aggregates content into a single file optimized for AI consumption

## Project Structure

```
web_scraper/
├── main.py                      # Entry point
├── config.py                    # Configuration management
├── scraper/
│   ├── __init__.py
│   ├── homepage.py              # Homepage scraper
│   ├── link_rewriter.py         # Link filtering and cleaning
│   ├── markdown_converter.py   # HTML to Markdown conversion
│   ├── ai_link_ranker.py        # AI-powered link prioritization
│   └── crawler.py               # Site crawler
├── utils/
│   ├── fetch.py                 # HTTP fetching utilities
│   └── logger.py                # Logging with colored output
└── output/                      # Scraped content saved here
    └── [site_name]/
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/ApexFutz/SiteSlayer.git
   cd SiteSlayer
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add your OpenAI API key (optional, but required for AI ranking):

   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Basic Usage

Run the scraper with a URL:

```bash
python web_scraper/main.py https://example.com
```

Or run interactively:

```bash
python web_scraper/main.py
# You will be prompted to enter a URL
```

### Example

```bash
python web_scraper/main.py https://python.org
```

This will:

1. Scrape the homepage
2. Extract and rank all internal links
3. Crawl up to 50 pages (configurable)
4. Save all content as Markdown files in `web_scraper/output/`

### Replicate Site Locally

After scraping, you can convert the markdown files to HTML and create a local replica:

```bash
python web_scraper/replicate_site.py
```

Or specify a custom output directory:

```bash
python web_scraper/replicate_site.py path/to/output
```

This will:

1. Convert all markdown files to styled HTML pages
2. Generate an index page linking to all scraped pages
3. Create a browsable local copy of the website

Open `web_scraper/output/index.html` in your browser to view the replicated site.

## Configuration

All settings can be configured via environment variables in the `.env` file:

### API Settings

- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered link ranking

### Scraping Settings

- `MAX_PAGES`: Maximum number of pages to scrape (default: 50)
- `TIMEOUT`: Request timeout in seconds (default: 30)
- `DELAY_BETWEEN_REQUESTS`: Delay between requests in seconds (default: 1.0)
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests (default: 5)

### Content Settings

- `MIN_CONTENT_LENGTH`: Minimum content length to save a page (default: 100)
- `INCLUDE_IMAGES`: Include images in markdown (default: true)

### AI Settings

- `USE_AI_RANKING`: Enable AI-powered link ranking (default: true)
- `AI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)

### Output Settings

- `OUTPUT_DIR`: Directory to save scraped content (default: web_scraper/output)

## Features in Detail

### AI-Powered Link Ranking

When enabled, SiteSlayer uses OpenAI to analyze and rank links based on:

- Content relevance
- Documentation pages
- Product/service pages
- Informational content priority

This ensures the most important pages are scraped first within the `MAX_PAGES` limit.

### Smart Content Extraction

The scraper intelligently identifies and extracts main content while removing:

- Navigation menus
- Headers and footers
- Sidebars
- Scripts and styles
- Advertisements

### Markdown Conversion

HTML content is converted to clean, readable Markdown with:

- Proper heading hierarchy
- Clean link formatting
- Preserved code blocks
- Formatted lists and tables

## Output

Scraped content is saved in two locations:

### Individual Files (`websites/`)

```
websites/
├── <domain>/
│   ├── homepage.md
│   ├── about.md
│   └── ...
```

Each file includes:

- Page title
- Source URL
- Markdown-formatted content

### Aggregated Content (`sites/`)

For AI chatbot integration, all content is automatically combined into a single file:

```
sites/
├── <domain>/
│   └── content.md
```

The `content.md` file contains:

- All pages combined with clear separators
- Complete metadata (titles, URLs, link text)
- Structured format optimized for AI consumption

See [MARKDOWN_AGGREGATION.md](MARKDOWN_AGGREGATION.md) for detailed documentation.

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError`

- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: No OpenAI API key error

- **Solution**: Either disable AI ranking (`USE_AI_RANKING=false`) or add your API key to `.env`

**Issue**: Connection timeout

- **Solution**: Increase the `TIMEOUT` value in `.env` or check your internet connection

**Issue**: Too many pages scraped

- **Solution**: Reduce `MAX_PAGES` in `.env`

## Requirements

See `requirements.txt` for all dependencies. Key packages include:

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: Fast HTML parsing
- `markdownify`: HTML to Markdown conversion
- `openai`: AI-powered features
- `python-dotenv`: Environment variable management
- `colorama`: Colored console output

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Roadmap

Future enhancements planned:

- [ ] Async/concurrent scraping for better performance
- [ ] Support for JavaScript-heavy websites
- [ ] Export to multiple formats (PDF, HTML, etc.)
- [ ] Advanced filtering options
- [ ] Rate limiting and retry logic
- [ ] Progress bars and better UI

## Author

Created by ApexFutz

## Acknowledgments

- BeautifulSoup for HTML parsing
- OpenAI for AI capabilities
- The Python community for excellent libraries

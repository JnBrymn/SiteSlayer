# SiteSlayer

A web scraper that extracts content from websites and converts it to Markdown. Also includes a web server to serve scraped sites.

## Installation

Requires Python 3.11.9+ and [UV](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/ApexFutz/SiteSlayer.git
cd SiteSlayer
uv sync
```

Optional: Set `OPENAI_API_KEY` in `.env` for AI-powered link ranking.

## Web Scraper

Scrapes websites and converts HTML content to Markdown files.

```bash
python web_scraper/main.py https://example.com
```

The scraper:
1. **Harvests HTML**: Downloads complete HTML content using Selenium (with JavaScript rendering) and saves to `sites/{domain}/index.html`
2. **Scrapes homepage**: Extracts markdown content from the homepage
3. **Crawls the site**: 
   - Extracts and ranks internal links (uses AI if `OPENAI_API_KEY` is set and `USE_AI_RANKING=true`)
   - Crawls up to `MAX_PAGES` pages (default: 5, configurable via `MAX_PAGES` env var)
   - Saves individual pages as Markdown files in `websites/{domain}/`
4. **Aggregates content**: Combines all markdown files into a single `content.md` file in `sites/{domain}/` for chatbot consumption

## Website Server

FastAPI server that serves scraped sites from the `sites/` directory. Each site can be accessed at `/site/{site_name}` and includes a chatbot widget.

Start locally:

```bash
./scripts/start_server.sh
```

Deploy to Fly.io:

```bash
./scripts/deploy_server.sh
```

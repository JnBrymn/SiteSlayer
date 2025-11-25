#!/bin/bash
# SiteSlayer - Website Scraper Script
# Usage: ./scripts/scrape.sh [URL]
# If URL is not provided, the script will prompt for input

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root directory
cd "$PROJECT_ROOT"

# Run the scraper with any provided arguments
# If no arguments are provided, Python script will prompt for input
python web_scraper/main.py "$@"


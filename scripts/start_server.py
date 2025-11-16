#!/usr/bin/env python3
"""
Script to start the SiteSlayer web server.
"""
import uvicorn
import sys
from pathlib import Path

# Add the project root to the path so we can import website_server
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    uvicorn.run(
        "website_server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )


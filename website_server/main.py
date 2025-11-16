"""
FastAPI web server for serving scraped sites from the sites/ directory.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SiteSlayer Web Server")

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the base directory (project root)
BASE_DIR = Path(__file__).parent.parent
SITES_DIR = BASE_DIR / "sites"


@app.get("/site/{site_path:path}")
async def serve_site(site_path: str):
    """
    Serve a site from the sites/ directory.
    
    Args:
        site_path: The site identifier (e.g., 'www.bigthunderevents.com')
                   Can include subdirectories if needed (e.g., 'www.example.com/subdir')
    
    Returns:
        The index.html file from the corresponding site directory.
    """
    # Normalize the path to prevent directory traversal attacks
    # Remove any leading/trailing slashes and normalize
    site_path = site_path.strip("/")
    
    # Prevent directory traversal
    if ".." in site_path or site_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid site path")
    
    # Construct the path to the site directory
    site_dir = SITES_DIR / site_path
    
    # Check if the directory exists
    if not site_dir.exists() or not site_dir.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Site '{site_path}' not found in sites directory"
        )
    
    # Look for index.html in the site directory
    index_file = site_dir / "index.html"
    
    if not index_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"index.html not found for site '{site_path}'"
        )
    
    # Serve the HTML file
    return FileResponse(
        index_file,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "SiteSlayer Web Server",
        "endpoints": {
            "serve_site": "/site/{site_path}",
            "example": "/site/www.bigthunderevents.com"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


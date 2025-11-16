"""
FastAPI web server for serving scraped sites from the sites/ directory.
Includes chatbot widget integration with mock endpoints.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

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
CHAT_BOT_DIR = Path(__file__).parent / "chat_bot"
CHAT_BOT_ASSETS_DIR = CHAT_BOT_DIR / "assets"


# Mock chat responses based on site and message content
def get_mock_chat_response(message: str, site: str) -> str:
    """Generate a mock chat response based on the message and site."""
    
    return f"Thank you for your message! I understand you're asking about '{message}'. Let me help you with that. Could you provide a bit more context so I can assist you better?"


# Middleware to inject chatbot script into HTML responses
class ChatbotInjectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only inject into HTML responses from /site/ endpoints
        if request.url.path.startswith("/site/") and response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # Read the response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                html_content = body.decode("utf-8", errors="ignore")
                
                # Inject chatbot script before </body>
                chatbot_script = '''
    <!-- SiteSlayer Chatbot Widget -->
    <script src="/chatbot/widget.js" data-id="default-chatbot" data-position="right"></script>
</body>'''
                
                if "</body>" in html_content:
                    html_content = html_content.replace("</body>", chatbot_script)
                else:
                    html_content += chatbot_script
                
                # Create new headers without Content-Length (it will be recalculated automatically)
                new_headers = {}
                for key, value in response.headers.items():
                    if key.lower() != "content-length":
                        new_headers[key] = value
                
                # Return modified response
                return Response(
                    content=html_content.encode("utf-8"),
                    status_code=response.status_code,
                    headers=new_headers,
                    media_type="text/html"
                )
        
        return response


app.add_middleware(ChatbotInjectionMiddleware)


# Chatbot endpoints

@app.get("/chatbot/widget.js")
async def serve_widget_js():
    """Serve the chatbot widget JavaScript."""
    widget_js_path = CHAT_BOT_DIR / "widget.js"
    if not widget_js_path.exists():
        raise HTTPException(status_code=404, detail="Widget JavaScript not found")
    return FileResponse(
        widget_js_path,
        media_type="application/javascript",
        headers={"Cache-Control": "public, max-age=3600"}
    )


@app.get("/chatbot/api/chatwidget/{uuid}/")
async def get_chatwidget_config(uuid: str):
    """Get chatbot widget configuration."""
    # Return mock configuration
    return {
        "chat_bubble_img": "/chatbot/assets/images/chat_bubble.png",
        "close": "/chatbot/assets/images/delete.png",
        "chat_bubble_color": "#DAE7FB",
        "user_msg_text_color": "#69707A",
        "default_icon": False,
        "show_popup_messages_only_once": True,
        "popup_type": None,  # Can be 'initial_messages_popup' or 'chatwidget_popup'
        "initial_message_popup_delay": -1,  # -1 means don't show
        "chatwidget_popup_delay": -1,
        "mobile_popup_type": None,
        "mobile_initial_message_popup_delay": -1,
        "mobile_chatwidget_popup_delay": -1,
        "mobile_initial_messages": [],
        "initial_messages": [
            "Hello! 👋 How can I help you today?",
            "Feel free to ask me anything about our services!"
        ],
        "font_family": "Montserrat, sans-serif",
        "font_size": 14,
        "size_of_widget": "medium"
    }


@app.get("/chatbot/embed/{uuid}")
async def serve_chat_interface(uuid: str, site: Optional[str] = None):
    """Serve the chat interface HTML page."""
    chat_interface_path = CHAT_BOT_DIR / "chat_interface.html"
    if not chat_interface_path.exists():
        raise HTTPException(status_code=404, detail="Chat interface not found")
    
    # Read the HTML template
    with open(chat_interface_path, "r") as f:
        html_content = f.read()
    
    # The UUID and site are already handled by JavaScript in the HTML
    # No need to modify the template
    
    return HTMLResponse(content=html_content)


@app.post("/chatbot/api/chats/")
async def handle_chat_message(request: Request, body: dict = Body(...)):
    """Handle chat messages and return mock responses."""
    message = body.get("message", "")
    site = body.get("site", "default")
    chatbot_uuid = body.get("chatbot_uuid", "default-chatbot") #TODO! I don't know why we need this
    user_key = body.get("user_key", "") #TODO! I don't know why we need this
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Generate mock response
    response_text = get_mock_chat_response(message, site)
    
    return {
        "response": response_text,
        "chatbot_uuid": chatbot_uuid,
        "site": site, #TODO! I don't think we need it. 
        "user_key": user_key
    }


# Static file serving for chatbot assets
@app.get("/chatbot/assets/{file_path:path}")
async def serve_chatbot_asset(file_path: str):
    """Serve chatbot static assets (CSS, images, etc.)."""
    asset_path = CHAT_BOT_ASSETS_DIR / file_path
    
    # Prevent directory traversal
    try:
        asset_path.resolve().relative_to(CHAT_BOT_ASSETS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Determine media type
    media_type = "application/octet-stream"
    if file_path.endswith(".css"):
        media_type = "text/css"
    elif file_path.endswith(".js"):
        media_type = "application/javascript"
    elif file_path.endswith(".png"):
        media_type = "image/png"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif file_path.endswith(".gif"):
        media_type = "image/gif"
    elif file_path.endswith(".svg"):
        media_type = "image/svg+xml"
    
    return FileResponse(
        asset_path,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"}
    )


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
            "example": "/site/www.bigthunderevents.com",
            "chatbot_widget": "/chatbot/widget.js",
            "chatbot_config": "/chatbot/api/chatwidget/{uuid}/",
            "chatbot_interface": "/chatbot/embed/{uuid}",
            "chatbot_api": "POST /chatbot/api/chats/"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


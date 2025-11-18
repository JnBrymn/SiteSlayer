# Chat Bot Assets

This directory contains assets downloaded from the chat widget on https://businesschatbot.site/

## Downloaded Assets

### JavaScript
- `js/chatbubble.js` - Main chat widget initialization script (20KB)

### CSS
- `css/chatwidget_styles.css` - Chat widget base styles (10KB)
- `css/chatwidget.css` - Additional chat widget styles (8.3KB)

### Images
- `images/chat_bubble.png` - Chat bubble icon (3.4KB)
- `images/delete.png` - Delete icon (1KB)
- `images/send-message-default.svg` - Send message icon (425B)
- `images/typing.gif` - Typing animation indicator (193KB)

## External Dependencies (CDN)

The chat widget also relies on these external resources loaded from CDNs:

- **Font Awesome 4.7.0** - Icon fonts
  - CSS: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css`
  - Fonts: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff2`

- **Bootstrap Icons 1.8.1** - Additional icon fonts
  - CSS: `https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.8.1/font/bootstrap-icons.min.css`
  - Fonts: `https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.8.1/font/fonts/bootstrap-icons.woff2`

- **Google Fonts - Montserrat** - Typography
  - CSS: `https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap`

- **Marked.js 2.0.3** - Markdown parser
  - JS: `https://cdn.jsdelivr.net/npm/marked@2.0.3/marked.min.js`

## Chat Widget API

The chat widget communicates with:
- Widget Embed URL: `/chatbot/embed/{site}?source=chatbubble`
- Widget Data API: `/chatbot/api/chatwidget/{site}/`
- Chat API: `POST /chatbot/api/chats/`

## Usage

To use these assets, you'll need to:
1. Include the JavaScript file: `chatbubble.js`
2. Include the CSS files: `chatwidget_styles.css` and `chatwidget.css`
3. Ensure external dependencies (Font Awesome, Bootstrap Icons, etc.) are loaded
4. Initialize the widget with the appropriate site identifier and configuration


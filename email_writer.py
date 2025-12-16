from pathlib import Path

BASE_DIR = Path(__file__).parent
SITES_DIR = BASE_DIR / "sites"

class EmailWriter:
    def __init__(self, site: str, history=None):
        """
        Initialize EmailWriter with site content

        Args:
            site: The site identifier
        """
        content_file = SITES_DIR / site / "content.md"
        if content_file.exists():
            with open(content_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            raise ValueError(f"Content file not found for site '{site}'")
        self.content = content
        self.site = site

    async def write(self, message):
        """
        Write an email using the site content.

        Args:
            message: The message/prompt for the email

        Returns:
            The email text - just the message for now
        """
        # For now, just return the message as specified by user
        return message

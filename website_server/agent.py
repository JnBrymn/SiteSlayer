from pathlib import Path

from agents import Agent, Runner


BASE_DIR = Path(__file__).parent.parent
SITES_DIR = BASE_DIR / "sites"

class ChatBot:
    def __init__(self, site: str):
        content_file = SITES_DIR / site / "content.md"
        if content_file.exists():
            with open(content_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            raise ValueError(f"Content file not found for site '{site}'")
        self.content = content

        self.agent = Agent(
            name="Assistant", 
            instructions=f"""\
You are a helpful assistant that can answer questions about the website {site}. The website content is:

{self.content}""")

    async def respond(self, message):
        result = await Runner.run(self.agent, message)
        return result.final_output
    
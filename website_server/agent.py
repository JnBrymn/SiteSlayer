from pathlib import Path

from agents import Agent, Runner


BASE_DIR = Path(__file__).parent.parent
SITES_DIR = BASE_DIR / "sites"

class ChatBot:
    def __init__(self, site: str, history=None):
        """
        Initialize ChatBot with site content and conversation history.
        
        Args:
            site: The site identifier
            history: List of previous messages in format [{"role": "user"|"assistant", "content": "..."}, ...]
        """
        content_file = SITES_DIR / site / "content.md"
        if content_file.exists():
            with open(content_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            raise ValueError(f"Content file not found for site '{site}'")
        self.content = content
        
        # Store conversation history
        self.history = history if history is not None else []

        self.agent = Agent(
            name="Assistant", 
            instructions=f"""\
You are a helpful assistant that can answer questions about the website {site}. The website content is:

{self.content}""")

    async def respond(self, message):
        """
        Respond to a message using the conversation history stored in the instance.
        
        Args:
            message: The current user message
        
        Returns:
            The agent's response text
        """
        # If we have history, format it for the agent
        # The agents library may need the history formatted in a specific way
        # For now, we'll include context from history in the message if available
        if self.history:
            # Format history as context
            history_context = "\n\nPrevious conversation:\n"
            for msg in self.history:
                role_label = "User" if msg.get("role") == "user" else "Assistant"
                history_context += f"{role_label}: {msg.get('content', '')}\n"
            
            # Append history context to the current message
            # Note: This is a simple approach. The agents library might have
            # better support for conversation history that we can use instead
            contextual_message = f"{history_context}\n\nCurrent message: {message}"
            result = await Runner.run(self.agent, contextual_message)
        else:
            result = await Runner.run(self.agent, message)
        
        return result.final_output
    
from fastmcp import Client
from google import genai
from google.genai.types import Content, Part
import asyncio
from dotenv import load_dotenv
import os
from fastmcp.client.elicitation import ElicitResult
import logging
from fastmcp.client.logging import LogMessage
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static
from textual.containers import Container, Vertical
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()
LOG_DIR = os.environ.get('LOG_FOLDER_PATH')
INSTRUCTION_PATH = os.environ.get('INSTRUCTION_PATH')

# Ensure directories for logs and data exist
if LOG_DIR:
    os.makedirs(LOG_DIR, exist_ok=True)
if INSTRUCTION_PATH:
    os.makedirs(os.path.dirname(INSTRUCTION_PATH), exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d")
LOG_DIR = os.environ.get('LOG_FOLDER_PATH')
LOG_FILE = f"mcpclient_log_{timestamp}.log"
log_file_path = os.path.join(LOG_DIR, LOG_FILE) if LOG_DIR else f"mcpclient_log_{timestamp}.log"

try:
    with open(INSTRUCTION_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read()
except (FileNotFoundError, TypeError):
    system_prompt = """You are an exceptionally helpful and friendly chatbot. 
    Your purpose is to provide concise and accurate information as requested by the user. 
    If a question is outside of your capabilities, politely inform the user that you are unable to help with that request.
    """

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
    ]
)


async def detailed_log_handler(message: LogMessage):
    msg = message.data.get('msg')
    extra = message.data.get('extra', 'No extra data')

    if message.level == "error":
        logging.error(f"ERROR: {msg} | Details: {extra}")
    elif message.level == "warning":
        logging.warning(f"WARNING: {msg} | Details: {extra}")
    else:
        logging.info(f"{message.level.upper()}: {msg} | Details: {extra}")


class ElicitationModal:
    """Stores elicitation request state."""

    def __init__(self):
        self.pending = False
        self.message = ""
        self.response_type = None
        self.future = None
        self.app_ref = None


elicitation_modal = ElicitationModal()


async def elicitation_handler(message: str, response_type: type, params, context):
    # Store the request and notify the TUI
    elicitation_modal.pending = True
    elicitation_modal.message = message
    elicitation_modal.response_type = response_type
    elicitation_modal.future = asyncio.Future()

    # Display the elicitation request in the TUI using call_later to avoid blocking
    if elicitation_modal.app_ref:
        def show_elicitation():
            try:
                chat_log = elicitation_modal.app_ref.query_one("#chat_log", RichLog)
                message_input = elicitation_modal.app_ref.query_one("#message_input", Input)

                chat_log.write(Panel(
                    Text(message, style="bold yellow"),
                    title="[bold yellow]⚠️  Server Request[/bold yellow]",
                    border_style="yellow"
                ))
                message_input.placeholder = "Type your response... (or 'cancel'/'decline')"
            except Exception:
                pass

        elicitation_modal.app_ref.call_later(show_elicitation)

    # Wait for the user to respond via the TUI
    result = await elicitation_modal.future

    # Clean up
    elicitation_modal.pending = False
    elicitation_modal.message = ""
    elicitation_modal.response_type = None
    elicitation_modal.future = None

    # Reset placeholder
    if elicitation_modal.app_ref:
        def reset_placeholder():
            try:
                message_input = elicitation_modal.app_ref.query_one("#message_input", Input)
                message_input.placeholder = "Type your message... (Ctrl+C to quit)"
            except Exception:
                pass

        elicitation_modal.app_ref.call_later(reset_placeholder)

    return result


class MCPChatApp(App):
    """A Textual TUI for MCP Client with Gemini."""

    CSS = """
    Screen {
        background: $surface;
    }

    #chat_container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #chat_log {
        height: 1fr;
        background: $surface;
        color: $text;
        padding: 1;
    }

    #input_container {
        height: auto;
        dock: bottom;
        padding: 0 1;
    }

    Input {
        margin: 1 0;
    }

    .user_message {
        color: $accent;
    }

    .ai_message {
        color: $success;
    }

    .system_message {
        color: $warning;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+l", "clear", "Clear Chat"),
    ]

    def __init__(self):
        super().__init__()
        self.message_history = []
        self.mcp_client = None
        self.gemini_client = None
        self.gemini_model = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical(id="chat_container"):
            yield RichLog(id="chat_log", highlight=True, markup=True, wrap=True)
        with Container(id="input_container"):
            yield Input(placeholder="Type your message... (Ctrl+C to quit)", id="message_input")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the MCP client and Gemini on mount."""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write(Panel("[bold cyan]Initializing MCP Client...[/bold cyan]"))

        # Set app reference for elicitation handler
        elicitation_modal.app_ref = self

        # Initialize clients
        self.mcp_client = Client(
            "http://mcpserver:8000/mcp",
            log_handler=detailed_log_handler,
            elicitation_handler=elicitation_handler
        )

        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.gemini_model = os.environ.get("GEMINI_MODEL")

        # Connect to MCP server
        await self.mcp_client.__aenter__()

        chat_log.write(Panel("[bold green]✓ Connected! Ready to chat.[/bold green]"))
        self.query_one("#message_input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission."""
        message_input = self.query_one("#message_input", Input)
        chat_log = self.query_one("#chat_log", RichLog)

        user_message = event.value.strip()
        if not user_message:
            return

        # Clear input
        message_input.value = ""

        # Check if this is a response to an elicitation request
        if elicitation_modal.pending:
            chat_log.write(Panel(
                Text(user_message, style="bold cyan"),
                title="[bold cyan]Your Response[/bold cyan]",
                border_style="cyan"
            ))

            # Create response and resolve the future
            if user_message.lower() in ["cancel", "decline"]:
                elicitation_modal.future.set_result(ElicitResult(action="decline"))
            else:
                response_data = elicitation_modal.response_type(value=user_message)
                elicitation_modal.future.set_result(response_data)
            return

        # Display user message
        chat_log.write(Panel(
            Text(user_message, style="bold cyan"),
            title="[bold cyan]You[/bold cyan]",
            border_style="cyan"
        ))

        # Add to history
        self.message_history.append(
            Content(role="user", parts=[Part(text=user_message)])
        )

        # Show thinking indicator
        chat_log.write("[italic yellow]Gemini is thinking...[/italic yellow]")

        # Run the API call without blocking the UI
        self.run_worker(self._generate_response(), exclusive=False)

    async def _generate_response(self):
        """Worker to generate response without blocking UI."""
        chat_log = self.query_one("#chat_log", RichLog)

        try:
            # Generate response (elicitation_handler may be called during this)
            response = await self.gemini_client.aio.models.generate_content(
                model=self.gemini_model,
                contents=self.message_history,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0,
                    tools=[self.mcp_client.session],
                    candidate_count=1,
                ),
            )

            # Add AI response to history
            model_response_content = response.candidates[0].content
            self.message_history.append(model_response_content)

            # Display AI response
            chat_log.write(Panel(
                Markdown(response.text),
                title="[bold green]Gemini[/bold green]",
                border_style="green"
            ))

        except Exception as e:
            chat_log.write(Panel(
                f"[bold red]Error: {str(e)}[/bold red]",
                title="[bold red]Error[/bold red]",
                border_style="red"
            ))

    def action_clear(self) -> None:
        """Clear the chat log."""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.clear()
        chat_log.write(Panel("[bold cyan]Chat cleared![/bold cyan]"))

    async def on_unmount(self) -> None:
        """Clean up when app closes."""
        if self.mcp_client:
            await self.mcp_client.__aexit__(None, None, None)


def main():
    """Run the TUI application."""
    app = MCPChatApp()
    app.run()


if __name__ == "__main__":
    main()
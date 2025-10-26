"""
MCP Client with WebSocket Interface

A FastAPI web application that provides a chat interface for interacting with
Google's Gemini AI model through the Model Context Protocol (MCP).

Usage:
    1. Set environment variables: GEMINI_API_KEY, GEMINI_MODEL
    2. Optional: LOG_FOLDER_PATH, INSTRUCTION_PATH
    3. Run: python <filename>.py
    4. Navigate to http://localhost:8080

Dependencies:
    - fastmcp: MCP client library
    - google-genai: Google Generative AI SDK
    - fastapi: Web framework
    - python-dotenv: Environment variable management
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.logging import LogMessage
from google import genai
from google.genai.types import Content, Part

# ============================================================================
# Configuration
# ============================================================================

load_dotenv()

DEFAULT_SYSTEM_PROMPT = """You are an exceptionally helpful and friendly chatbot. 
Your purpose is to provide concise and accurate information as requested by the user. 
If a question is outside of your capabilities, politely inform the user that you are unable to help with that request.
"""

# Configure logging directory and file path
log_dir = os.environ.get('LOG_FOLDER_PATH')
if log_dir:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / f"mcpclient_log_{datetime.now().strftime('%Y-%m-%d')}.log"
else:
    log_path = Path(f"mcpclient_log_{datetime.now().strftime('%Y-%m-%d')}.log")

# Setup file-based logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_path)]
)
logger = logging.getLogger(__name__)

# Load system prompt from file or use default
instruction_path = os.environ.get('INSTRUCTION_PATH')
if instruction_path:
    try:
        system_prompt = Path(instruction_path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        system_prompt = DEFAULT_SYSTEM_PROMPT
else:
    system_prompt = DEFAULT_SYSTEM_PROMPT

# ============================================================================
# State Management
# ============================================================================


class ElicitationState:
    """
    Manages user elicitation requests from MCP servers.

    Elicitation occurs when an MCP tool needs additional user input during execution.
    This class coordinates the request/response flow between MCP and the WebSocket.
    """

    def __init__(self):
        self.pending = False  # Whether an elicitation is currently active
        self.message = ""  # The question/prompt to show the user
        self.response_type = None  # Expected type of user's response
        self.future: Optional[asyncio.Future] = None  # Resolves when user responds
        self.websocket = None  # Active WebSocket connection


class ConnectionState:
    """
    Per-connection state for each WebSocket client.

    Isolates conversation history and clients per user to support
    multiple simultaneous chat sessions.
    """

    def __init__(self):
        self.message_history = []  # Conversation history (user + assistant messages)
        self.mcp_client = None  # MCP client instance for this connection
        self.gemini_client = None  # Gemini AI client for this connection


# Global state - shared across the application
elicitation_state = ElicitationState()
connections: Dict[int, ConnectionState] = {}  # Maps WebSocket ID -> ConnectionState

# ============================================================================
# MCP Handlers
# ============================================================================


async def log_handler(message: LogMessage) -> None:
    """
    Handle log messages from MCP client.

    Routes MCP client logs to our application logger with appropriate severity.
    """
    msg = message.data.get('msg', 'No message')
    extra = message.data.get('extra', 'No extra data')

    if message.level == "error":
        logger.error(f"MCP: {msg} | {extra}")
    elif message.level == "warning":
        logger.warning(f"MCP: {msg} | {extra}")
    else:
        logger.info(f"MCP: {msg} | {extra}")


async def elicitation_handler(message: str, response_type: type, params: Any, context: Any) -> Any:
    """
    Handle elicitation requests from MCP tools.

    When an MCP tool needs user input, this function:
    1. Sends the request to the web client via WebSocket
    2. Waits (blocks) for the user to respond
    3. Returns the response to the MCP tool so it can continue

    This enables interactive workflows where tools can ask follow-up questions.
    """
    if not elicitation_state.websocket:
        raise RuntimeError("No WebSocket connection for elicitation")

    # Store elicitation request in global state
    elicitation_state.pending = True
    elicitation_state.message = message
    elicitation_state.response_type = response_type
    elicitation_state.future = asyncio.Future()

    try:
        # Send elicitation prompt to web client
        await elicitation_state.websocket.send_json({
            "type": "elicitation",
            "message": message
        })

        # Block until user responds (future is resolved in websocket_endpoint)
        return await elicitation_state.future
    finally:
        # Clean up state regardless of success or failure
        elicitation_state.pending = False
        elicitation_state.message = ""
        elicitation_state.response_type = None
        elicitation_state.future = None


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI()

# Serve static files (HTML, CSS, JS) from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_index() -> HTMLResponse:
    """Serve the main chat interface HTML page."""
    try:
        html_content = Path("static/index.html").read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        logger.error("static/index.html not found")
        return HTMLResponse(content="<h1>Error: index.html not found</h1>", status_code=500)


async def generate_response(conn_state: ConnectionState, gemini_model: str, websocket: WebSocket) -> None:
    """
    Generate AI response using Gemini with MCP tool access.

    This runs as a background task to allow the WebSocket loop to continue
    handling messages (especially elicitation responses). The AI can call MCP
    tools which may trigger elicitation, pausing generation until the user responds.
    """
    try:
        # Call Gemini API with conversation history and MCP tools
        response = await conn_state.gemini_client.aio.models.generate_content(
            model=gemini_model,
            contents=conn_state.message_history,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,  # Deterministic responses
                tools=[conn_state.mcp_client.session],  # Give AI access to MCP tools
                candidate_count=1,
            ),
        )

        # Add AI response to conversation history
        conn_state.message_history.append(response.candidates[0].content)

        # Send completed response to client
        await websocket.send_json({"type": "assistant", "message": response.text})

    except Exception as e:
        logger.exception(f"Error generating response: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time chat communication.

    Handles the complete chat session lifecycle:
    - Connection initialization (MCP and Gemini clients)
    - Message exchange (user messages -> AI responses)
    - Elicitation flow (when tools need user input)
    - Session management (reset chat history)
    - Cleanup (close connections, remove state)

    Message types from client:
        - "message": User sends a chat message
        - "elicitation_response": User responds to tool's request for input
        - "reset": Clear the conversation history
    """
    await websocket.accept()

    # Create isolated state for this connection
    conn_state = ConnectionState()
    conn_id = id(websocket)
    connections[conn_id] = conn_state
    elicitation_state.websocket = websocket

    try:
        # ====================================================================
        # Initialize MCP and Gemini clients
        # ====================================================================

        await websocket.send_json({"type": "system", "message": "Initializing..."})

        # Create MCP client (connects to MCP server for tool access)
        conn_state.mcp_client = Client(
            "http://mcpserver:8000/mcp",  # Assumes Docker service named 'mcpserver'
            log_handler=log_handler,
            elicitation_handler=elicitation_handler
        )

        # Get required environment variables
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        gemini_model = os.environ.get("GEMINI_MODEL")

        if not gemini_api_key or not gemini_model:
            raise ValueError("GEMINI_API_KEY and GEMINI_MODEL must be set")

        # Create Gemini client and start MCP session
        conn_state.gemini_client = genai.Client(api_key=gemini_api_key)
        await conn_state.mcp_client.__aenter__()

        await websocket.send_json({"type": "system", "message": "✓ Connected! Ready to chat."})

        # ====================================================================
        # Main message loop - process messages from client
        # ====================================================================

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "message":
                # User sent a chat message
                user_message = data["message"]

                # Echo message back for display
                await websocket.send_json({"type": "user", "message": user_message})

                # Add to conversation history
                conn_state.message_history.append(
                    Content(role="user", parts=[Part(text=user_message)])
                )

                # Show thinking indicator
                await websocket.send_json({"type": "thinking", "message": "Thinking..."})

                # Start AI generation as background task (allows handling elicitation)
                asyncio.create_task(generate_response(conn_state, gemini_model, websocket))

            elif msg_type == "elicitation_response":
                # User responded to a tool's request for input
                user_response = data["message"]

                # Echo response back for display
                await websocket.send_json({"type": "user", "message": user_response})

                # Resolve the pending elicitation future (unblocks the tool)
                if elicitation_state.pending and elicitation_state.future:
                    if user_response.lower() in ["cancel", "decline"]:
                        # User declined to provide input
                        elicitation_state.future.set_result(ElicitResult(action="decline"))
                    else:
                        # Wrap response in expected type and return to tool
                        response_data = elicitation_state.response_type(value=user_response)
                        elicitation_state.future.set_result(response_data)

            elif msg_type == "reset":
                # Clear conversation history (start fresh)
                conn_state.message_history = []
                await websocket.send_json({"type": "system", "message": "Chat history cleared"})

    except WebSocketDisconnect:
        # Client disconnected normally
        logger.info(f"WebSocket {conn_id} disconnected")

    except ValueError as e:
        # Configuration error (missing env vars)
        logger.error(f"Configuration error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})

    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error: {e}")

    finally:
        # ====================================================================
        # Cleanup - close connections and remove state
        # ====================================================================

        # Close MCP client session gracefully
        if conn_state.mcp_client:
            try:
                await conn_state.mcp_client.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing MCP client: {e}")

        # Remove from active connections
        connections.pop(conn_id, None)

        # Clear elicitation state if this was the active websocket
        if elicitation_state.websocket is websocket:
            elicitation_state.websocket = None


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on 0.0.0.0:8080")
    logger.info(f"Log file: {log_path}")
    uvicorn.run(app, host="0.0.0.0", port=8080)
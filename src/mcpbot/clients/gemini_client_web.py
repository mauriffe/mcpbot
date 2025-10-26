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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
from typing import Optional

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


class ElicitationState:
    """Stores elicitation request state."""

    def __init__(self):
        self.pending = False
        self.message = ""
        self.response_type = None
        self.future: Optional[asyncio.Future] = None
        self.websocket = None


elicitation_state = ElicitationState()


async def detailed_log_handler(message: LogMessage):
    msg = message.data.get('msg')
    extra = message.data.get('extra', 'No extra data')

    if message.level == "error":
        logging.error(f"ERROR: {msg} | Details: {extra}")
    elif message.level == "warning":
        logging.warning(f"WARNING: {msg} | Details: {extra}")
    else:
        logging.info(f"{message.level.upper()}: {msg} | Details: {extra}")


async def elicitation_handler(message: str, response_type: type, params, context):
    # Store the request and notify the web client
    elicitation_state.pending = True
    elicitation_state.message = message
    elicitation_state.response_type = response_type
    elicitation_state.future = asyncio.Future()

    # Send elicitation request to web client
    if elicitation_state.websocket:
        await elicitation_state.websocket.send_json({
            "type": "elicitation",
            "message": message
        })

    # Wait for the user to respond
    result = await elicitation_state.future

    # Clean up
    elicitation_state.pending = False
    elicitation_state.message = ""
    elicitation_state.response_type = None
    elicitation_state.future = None

    return result


# Initialize FastAPI
app = FastAPI()


# Store active connections and their state
class ConnectionState:
    def __init__(self):
        self.message_history = []
        self.mcp_client = None
        self.gemini_client = None
        self.generation_task = None


connections = {}


async def generate_response(conn_state, gemini_model, websocket):
    """Generate AI response - runs as a separate task."""
    try:
        # Generate response (elicitation may happen during this)
        response = await conn_state.gemini_client.aio.models.generate_content(
            model=gemini_model,
            contents=conn_state.message_history,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                tools=[conn_state.mcp_client.session],
                candidate_count=1,
            ),
        )

        # Add AI response to history
        model_response_content = response.candidates[0].content
        conn_state.message_history.append(model_response_content)

        # Send response
        await websocket.send_json({"type": "assistant", "message": response.text})

    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})


# HTML page
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Chat Client</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.assistant {
            align-self: flex-start;
            background: #f0f0f0;
            color: #333;
            border-bottom-left-radius: 4px;
        }

        .message.system {
            align-self: center;
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
            font-style: italic;
            max-width: 80%;
        }

        .message.elicitation {
            align-self: center;
            background: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
            font-weight: bold;
            max-width: 80%;
        }

        .thinking {
            align-self: flex-start;
            color: #999;
            font-style: italic;
            padding: 10px;
        }

        .chat-input-container {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }

        #messageInput {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }

        #messageInput:focus {
            border-color: #667eea;
        }

        #sendButton {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }

        #sendButton:hover {
            transform: scale(1.05);
        }

        #sendButton:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .status {
            padding: 10px 20px;
            background: #d4edda;
            border-bottom: 1px solid #c3e6cb;
            color: #155724;
            text-align: center;
            font-size: 14px;
        }

        .status.error {
            background: #f8d7da;
            border-bottom-color: #f5c6cb;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">MCP Chat Client</div>
        <div id="status" class="status">Connecting...</div>
        <div class="chat-messages" id="messages"></div>
        <div class="chat-input-container">
            <input type="text" id="messageInput" placeholder="Type your message..." disabled>
            <button id="sendButton" disabled>Send</button>
        </div>
    </div>

    <script>
        let ws;
        let isElicitationPending = false;

        function connect() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);

            ws.onopen = () => {
                document.getElementById('status').textContent = '✓ Connected';
                document.getElementById('status').className = 'status';
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };

            ws.onclose = () => {
                document.getElementById('status').textContent = '✗ Disconnected';
                document.getElementById('status').className = 'status error';
                document.getElementById('messageInput').disabled = true;
                document.getElementById('sendButton').disabled = true;
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }

        function handleMessage(data) {
            const messagesDiv = document.getElementById('messages');

            if (data.type === 'system') {
                addMessage(data.message, 'system');
            } else if (data.type === 'user') {
                addMessage(data.message, 'user');
            } else if (data.type === 'assistant') {
                // Remove thinking indicator
                const thinking = messagesDiv.querySelector('.thinking');
                if (thinking) thinking.remove();

                addMessage(data.message, 'assistant');
            } else if (data.type === 'thinking') {
                addMessage(data.message, 'thinking');
            } else if (data.type === 'elicitation') {
                isElicitationPending = true;
                addMessage('⚠️ ' + data.message, 'elicitation');
                document.getElementById('messageInput').placeholder = 'Type your response... (or type "cancel")';
            } else if (data.type === 'error') {
                addMessage('Error: ' + data.message, 'system');
            }
        }

        function addMessage(text, className) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${className}`;
            messageDiv.textContent = text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message) return;

            ws.send(JSON.stringify({
                type: isElicitationPending ? 'elicitation_response' : 'message',
                message: message
            }));

            input.value = '';

            if (isElicitationPending) {
                isElicitationPending = false;
                document.getElementById('messageInput').placeholder = 'Type your message...';
            }
        }

        document.getElementById('sendButton').addEventListener('click', sendMessage);
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        connect();
    </script>
</body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(HTML_PAGE)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Create connection state
    conn_state = ConnectionState()
    connections[id(websocket)] = conn_state
    elicitation_state.websocket = websocket

    try:
        # Initialize MCP and Gemini clients
        await websocket.send_json({"type": "system", "message": "Initializing MCP Client..."})

        conn_state.mcp_client = Client(
            "http://mcpserver:8000/mcp",
            log_handler=detailed_log_handler,
            elicitation_handler=elicitation_handler
        )

        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        conn_state.gemini_client = genai.Client(api_key=gemini_api_key)
        gemini_model = os.environ.get("GEMINI_MODEL")

        await conn_state.mcp_client.__aenter__()

        await websocket.send_json({"type": "system", "message": "✓ Connected! Ready to chat."})

        # Handle messages
        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                user_message = data["message"]

                # Echo user message
                await websocket.send_json({"type": "user", "message": user_message})

                # Add to history
                conn_state.message_history.append(
                    Content(role="user", parts=[Part(text=user_message)])
                )

                # Show thinking
                await websocket.send_json({"type": "thinking", "message": "Gemini is thinking..."})

                # Start the generation task
                generation_task = asyncio.create_task(generate_response(conn_state, gemini_model, websocket))

                # Store task reference so elicitation can work
                conn_state.generation_task = generation_task

            elif data["type"] == "elicitation_response":
                user_response = data["message"]

                # Echo the elicitation response
                await websocket.send_json({"type": "user", "message": user_response})

                # Resolve the elicitation future
                if elicitation_state.pending and elicitation_state.future:
                    if user_response.lower() in ["cancel", "decline"]:
                        elicitation_state.future.set_result(ElicitResult(action="decline"))
                    else:
                        response_data = elicitation_state.response_type(value=user_response)
                        elicitation_state.future.set_result(response_data)

                # The generation_task will continue automatically after the future resolves

    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        if conn_state.mcp_client:
            await conn_state.mcp_client.__aexit__(None, None, None)
        if id(websocket) in connections:
            del connections[id(websocket)]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
# MCPBot

A Model Context Protocol (MCP) server with multiple Gemini AI client interfaces, all containerized with Docker.

## Overview

MCPBot is a project that demonstrates the Model Context Protocol architecture with:
- **MCP Server**: Provides tools for dice rolling, calculations, and weather information
- **Multiple Clients**: Three different client implementations (Web UI, Terminal UI, and Basic)
- **Docker-based**: Fully containerized for easy deployment and development

## Features

### MCP Server Tools
- **Dice Roller**: Roll multiple dice with user confirmation
- **Calculator**: Perform basic arithmetic operations
- **Weather**: Get real-time weather information for multiple cities using Open-Meteo API

### Client Implementations
1. **Web Interface** (`gemini_client.py`): Modern WebSocket-based chat interface accessible via browser
2. **Terminal UI** (`gemini_client_tui.py`): Rich terminal interface using Textual
3. **Basic Client** (`fastmcp_client.py`): Simple command-line client for testing

## Architecture

```
┌─────────────────────┐
│   Gemini AI Model   │
│   (via API)         │
└──────────┬──────────┘
           │
           │ Uses tools via MCP
           │
┌──────────▼──────────┐
│   MCP Server        │
│   (Port 8000)       │
│   - Dice Tools      │
│   - Calc Tools      │
│   - Weather Tools   │
└─────────────────────┘
           ▲
           │ MCP Protocol
           │
┌──────────┴──────────┐
│   Client            │
│   (Port 8080)       │
│   - Web/TUI/CLI     │
└─────────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)
- Gemini API Key ([Get one here](https://aistudio.google.com/api-keys))

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd mcpbot
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   LOG_FOLDER_PATH=/usr/src/app/logs
   INSTRUCTION_PATH=/usr/src/app/data/system_instruction.txt
   ```

3. **Build and start services**
   ```bash
   make setup-and-go
   ```

4. **Access the web interface**
   Open your browser to: `http://localhost:8080`

## Usage

### Using Make Commands

The project includes a Makefile for convenient operations:

```bash
# Build all Docker images
make build

# Start the MCP server
make start-server

# Start the client
make start-client

# View logs
make logs

# Stop services
make stop

# Stop and remove all containers
make down

# Clean up everything (containers + images)
make clean-all

# Build and start everything
make setup-and-go

# Clean all, rebuild and start everything
make rebuild
```

### Manual Docker Compose Commands

```bash
# Build images
docker-compose build

# Start server
docker-compose up -d mcpserver

# Start client
docker-compose up -d client

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## Client Interfaces

### Web Client (Default)
- **URL**: http://localhost:8080
- **Features**: 
  - Real-time chat interface
  - WebSocket communication
  - Message history
  - Reset conversation button
  - Elicitation support (tool confirmation prompts)

### Terminal UI Client
To use the TUI instead, modify `client.Dockerfile` to use:
```dockerfile
CMD ["python", "gemini_client_tui.py"]
```

### Basic CLI Client
For testing, modify `client.Dockerfile` to use:
```dockerfile
CMD ["python", "fastmcp_client.py"]
```

## Project Structure

```
mcpbot/
├── src/
│   └── mcpbot/
│       ├── server/
│       │   ├── server.py          # MCP server main
│       │   ├── tools/
│       │   │   ├── dice_tools.py  # Dice rolling tool
│       │   │   ├── calcul_tools.py # Calculator tool
│       │   │   └── weather_tools.py # Weather API tool
│       │   ├── prompts/           # (Future) MCP prompts
│       │   └── resources/         # (Future) MCP resources
│       └── clients/
│           ├── gemini_client.py   # Web interface client
│           ├── gemini_client_tui.py # Terminal UI client
│           ├── fastmcp_client.py  # Basic CLI client
│           └── static/            # Web UI assets
│               ├── index.html
│               ├── styles.css
│               └── app.js
├── dock/
│   ├── data/
│   │   └── system_instruction.txt # AI system prompt
│   └── logs/                      # Application logs
├── docker-compose.yml
├── server.Dockerfile
├── client.Dockerfile
├── Makefile
├── pyproject.toml
└── .env.example
```

## Configuration

### System Instructions
Customize the AI's behavior by editing `dock/data/system_instruction.txt`:

```text
You are an exceptionally helpful and friendly chatbot. 
Your purpose is to provide concise and accurate information when rolling dice as requested by the user.
You should only use the available tools to answer these types of questions. 
If a question is outside of your capabilities, politely inform the user that you are unable to help with that request.
```

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `GEMINI_MODEL`: Model to use (default: gemini-2.5-flash)
- `LOG_FOLDER_PATH`: Path for log files
- `INSTRUCTION_PATH`: Path to system instruction file

## Development

### Adding New Tools

1. Create a new tool file in `src/mcpbot/server/tools/`:
```python
from mcp import types
from pydantic import BaseModel, Field

def register_my_tools(mcp):
    @mcp.tool(
        name="my_tool",
        description="Description of what this tool does"
    )
    def handle_my_tool(arguments: dict) -> list[types.TextContent]:
        # Your tool logic here
        return [types.TextContent(type="text", text="Result")]
```

2. Register it in `server.py`:
```python
from tools.my_tools import register_my_tools
register_my_tools(mcpbot)
```

### Logs

Application logs are stored in `dock/logs/`:
- Server logs: `mcpserver_log_YYYY-MM-DD.log`
- Client logs: `mcpclient_log_YYYY-MM-DD.log`

## Technology Stack

- **MCP Protocol**: Model Context Protocol for AI-tool integration
- **FastMCP**: Python MCP server framework
- **Google Gemini**: AI language model
- **FastAPI**: Web framework for client interface
- **Textual**: Terminal UI framework
- **Docker**: Containerization
- **WebSockets**: Real-time communication

## Troubleshooting

### Client can't connect to server
- Ensure the server is running: `docker-compose ps`
- Check server logs: `docker-compose logs mcpserver`
- Verify network connectivity between containers

### API Key Issues
- Verify your Gemini API key is set in `.env`
- Check if the key has proper permissions
- Ensure the `.env` file is in the project root

### Port Conflicts
- Default ports: 8000 (server), 8080 (client)
- Change ports in `docker-compose.yml` if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

TODO

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Google Gemini](https://ai.google.dev/)
- Weather data from [Open-Meteo](https://open-meteo.com/)

## Contact

TODO
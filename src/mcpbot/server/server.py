from fastmcp import FastMCP
from tools.calcul_tools import register_calcul_tools
from tools.dice_tools import register_dice_tools
from tools.weather_tools import register_weather_tools
from fastmcp.utilities.logging import get_logger
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Configure file logging
timestamp = datetime.now().strftime("%Y-%m-%d")
LOG_DIR = os.environ.get('LOG_FOLDER_PATH')
# Ensure directories for logs and data exist
if LOG_DIR:
    os.makedirs(LOG_DIR, exist_ok=True)
# Get the folder path
LOG_FILE = f"mcpserver_log_{timestamp}.log"
log_file_path = os.path.join(LOG_DIR, LOG_FILE)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path)
    ]
)

to_client_logger = get_logger(name="fastmcp.server.context.to_client")
to_client_logger.setLevel(level=logging.DEBUG)

mcpbot = FastMCP(
    name="HelpfulAssistant",
    instructions = """
        This server provides data tools.
    """,
)
# Register tools
register_calcul_tools(mcpbot)
register_dice_tools(mcpbot)
register_weather_tools(mcpbot)

if __name__ == "__main__":
    try:
        logging.info("Starting MCP server on http://0.0.0.0:8000/mcp")
        mcpbot.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
    except KeyboardInterrupt:
        logging.info("Shutting down MCP server...")
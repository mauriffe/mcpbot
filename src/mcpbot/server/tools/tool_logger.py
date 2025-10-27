"""
Tool Logger - Send messages from MCP tools to client UI.
"""
from typing import Optional
from fastmcp import Context

class ToolLogger:
    """Logger that sends messages from tools to the client UI."""

    @staticmethod
    async def log_to_client(ctx: Context, message: str, level: str = "info"):
        """
        Send a log message to the client.

        Args:
            ctx: FastMCP context
            message: Message to display
            level: Log level (info, success, warning, error, debug)
        """
        # Use FastMCP's logging to send to client
        if level == "error":
            await ctx.error(message, extra={"display_in_ui": True})
        elif level == "warning":
            await ctx.warning(message, extra={"display_in_ui": True})
        else:
            await ctx.info(message,extra={"display_in_ui": True})
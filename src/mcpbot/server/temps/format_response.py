from mcp import types
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from helpers.db_helper import get_conn
from helpers.tool_logger import ToolLogger
from fastmcp import Context
from dotenv import load_dotenv
import os
from helpers.prompts import RESPONSE_FORMATTING_PROMPT
import json

################################
# Configuration and Initialization 
################################

load_dotenv()
POSTGRES_DB = os.environ.get('POSTGRES_DB')
logger = logging.getLogger(__name__)

################################
# Helper Functions
################################

async def _format_natural_response(user_question: str, sql_query: str,
                            results: List[Dict], ctx: Context) -> str:
    """Formats the response in natural language."""
    try:
        filled_prompt = RESPONSE_FORMATTING_PROMPT.format(
            question=user_question,
            sql=sql_query,
            count=len(results),
            results=json.dumps(results, indent=2, ensure_ascii=False, default=str)
        )

        # Request LLM analysis
        response = await ctx.sample(filled_prompt)

        selected = response.text.strip().lower()

        return response
    except Exception as e:
        logger.error(f"Response formatting error: {e}")
        return f"I found {len(results)} result(s) for your question."


################################
# Tool Registration
################################

def register_format_response_tools(mcp):
    """
    Register the format_response tool with the MCP server.

    """
    @mcp.tool(
    name="step7_format_response",
    description="Step 7: Formats the final response in natural language based on the user's question, executed SQL query, and results.",
    tags={"table", "format", "final", "step7"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="Step7 Format Response Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def step7_format_response(user_question: str, sql_query: str, results: List[Dict], ctx: Context) -> Dict[str, Any]:
        """Step 7: Formats the final response in natural language"""
        try:
            natural_response = await _format_natural_response(user_question, sql_query, results, ctx)
            return {
                "step": 7,
                "action": "format_response",
                "status": "success",
                "user_question": user_question,
                "sql_query": sql_query,
                "results_count": len(results),
                "natural_response": natural_response,
                "message": "✅ Response formatted in natural language"
            }
        except Exception as e:
            return {
                "step": 7,
                "action": "format_response",
                "status": "error",
                "error": str(e),
                "message": f"❌ Error during formatting: {str(e)}"
            }
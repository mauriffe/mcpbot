"""
Tool for selecting the most appropriate table from a list of database tables based on a user question.
"""

from mcp import types
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from db_helper import get_conn
from .tool_logger import ToolLogger
from fastmcp import Context
from dotenv import load_dotenv
import os

################################
# Configuration and Initialization
################################

load_dotenv()
POSTGRES_DB = os.environ.get('POSTGRES_DB')
logger = logging.getLogger(__name__)

TABLE_SELECTION_PROMPT = """You are a database table selection expert. Your job is to select the most relevant table based on the user's question.

<task>
CRITICAL PRIORITY: If the user explicitly mentions a table name in their question (e.g., "from the employees table", "search in users"), that table MUST be selected if it exists in the provided list. This is an ABSOLUTE and NON-NEGOTIABLE rule that overrides all other semantic analysis.
</task>

<context>
User Question: "{question}"
Database: {database}
Available Tables: {tables}
</context>

<instructions>
**STEP 1 - MANDATORY TABLE NAME SCAN (HIGHEST PRIORITY):**
Carefully scan the user's question for ANY explicit mention of a table name. Check for:
- Exact table names from the list (e.g., "employees").
- Singular/plural variations ("employee" vs "employees").
- Mentions like "in the 'products' table".

**STEP 2 - VALIDATION AGAINST AVAILABLE TABLES:**
- **IF** you find a mentioned table name in the user question, check if it exists in the 'Available Tables' list.
- If it exists, you MUST select that table. For example, if the user says "use employees" and the table "employees" is in the list, you select "employees". THIS IS MANDATORY.

**STEP 3 - FALLBACK (ONLY if NO table name is explicitly mentioned):**
- If and only if the user did not mention any table name, analyze the entities and concepts in the question (e.g., "who are the customers" -> likely 'customers' table).
- Select the most semantically relevant table from the list.
</instructions>

<output_format>
Respond with ONLY the exact table name from the available list. No explanations.
</output_format>"""


################################
# Helper Functions
################################

async def _select_best_table(user_question: str, tables: List[str], ctx: Context, database: str = POSTGRES_DB) -> str:
    """Uses AI to select the best table."""
    if len(tables) == 1:
        return tables[0] if tables else "unknown"
    try:
        filled_prompt = TABLE_SELECTION_PROMPT.format(
            question=user_question,
            database=database,
            tables=tables
        )

        # Request LLM analysis
        response = await ctx.sample(filled_prompt)

        selected = response.text.strip().strip('"').strip("'").lower()

        logger.info(f"AI selected table: {response.text}")
        if selected in tables:
            return selected
        else:
            logger.warning(f"AI chose invalid '{selected}', using {tables[0]}")
            return tables[0]
    except Exception as e:
        logger.error(f"Table selection error: {e}")
        return tables[0]


class SeelectBestTableResult(BaseModel):
    """Structured result for the select_best_table tool (step2_select_table)."""
    step: int = Field(description="Step number")
    action: str = Field(description="Action name")
    status: str = Field(description="'success' or 'error'")
    database: str = Field(description="Database name")
    selected_table: Optional[str] = Field(None, description="The table selected as best fit for the question")
    available_tables: List[str] = Field(default_factory=list, description="List of available table names")
    message: str = Field(description="Human-friendly message")
    error: Optional[str] = Field(None, description="Error message when status=='error'")


################################
# Tool Registration
################################

def register_select_best_table_tools(mcp):
    """
    Register all table selection tools with the MCP server.

    This function sets up the table selection toolset, including:
    - Step 2: Select Best table (step2_select_table)

    Args:
        mcp: The MCP server instance to register tools with.

    Note:
        Tools are registered with appropriate metadata, tags, and annotations
        for proper integration with the MCP framework.
    """

    @mcp.tool(
        name="step2_select_table",
        description="Select tables in the specified PostgreSQL database.",
        tags={"table", "selection", "step2"},  # Optional tags for organization/filtering
        meta={"version": "1.2", "author": "martin"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Step2 Select Tables Tool",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=False,
            # If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
            openWorldHint=False,
            # If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
        )
    )
    async def step2_select_table(user_question: str, tables: List[str], ctx: Context,
                                 database: str = POSTGRES_DB) -> SeelectBestTableResult:
        """Step 2: Selects the best table for the question"""
        try:
            await ToolLogger.log_to_client(
                ctx,
                f"Selecting best table in database '{database}'...",
                "info"
            )
            selected_table = await _select_best_table(user_question=user_question, tables=tables, database=database,
                                                      ctx=ctx)
            return SeelectBestTableResult(
                step=2,
                action="select_table",
                status="success",
                database=database,
                selected_table=selected_table,
                available_tables=tables,
                message=f"✅ Selected table: '{selected_table}' in '{database}'"
            )
        except Exception as e:
            return SeelectBestTableResult(
                step=2,
                action="select_table",
                status="error",
                database=database,
                selected_table=None,
                available_tables=tables,
                message=f"❌ Error during table selection: {str(e)}",
                error=str(e)
            )

"""
Database Table Schema Analysis Tool

This module provides functionality to analyze the schema of a specific table in a PostgreSQL database.
It is part of the MCP (Model Context Protocol) toolset for database introspection and automation.

Key Features:
- Asynchronously describes the columns of a table, including data type, nullability, default, and comments.
- Returns results in a structured Pydantic model for downstream processing.
- Integrates with the MCP server as a registered tool.
"""


# Imports
from mcp import types
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from helpers.db_helper import get_conn
from helpers.tool_logger import ToolLogger
from fastmcp import Context
from dotenv import load_dotenv
import os


################################
# Configuration and Initialization
################################


load_dotenv()  # Load environment variables from .env file
POSTGRES_DB = os.environ.get('POSTGRES_DB')  # Default database name from environment
logger = logging.getLogger(__name__)  # Module-level logger


################################
## Helper Functions
################################

async def describe_table(database: str, table: str) -> List[Dict[str, Any]]:
    """
    Retrieve the schema of a table from the specified PostgreSQL database.

    Args:
        database (str): Name of the database to connect to.
        table (str): Name of the table to describe.

    Returns:
        List[Dict[str, Any]]: List of dictionaries, each representing a column and its properties.
    """
    try:
        with get_conn(database) as conn, conn.cursor() as cur:
            # Query information_schema for column details and comments
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default, col_description((table_schema || '.' || table_name)::regclass, ordinal_position) AS column_comment
                FROM information_schema.columns
                WHERE table_schema='public' AND table_name=%s
                ORDER BY ordinal_position;
                """,
                (table,)
            )

            # Build schema list from query results
            schema = [
                {
                    "column_name": row[0],
                    "data_type": row[1],
                    "is_nullable": row[2] == "YES",
                    "column_default": row[3],
                    "column_comment": row[4],
                }
                for row in cur.fetchall()
            ]

            logger.info(f"Schema of {table}: {len(schema)} columns")
            return schema
    except Exception as e:
        logger.error(f"Table description error: {e}")
        return []

class AnalyzeSchemaResult(BaseModel):
    """
    Pydantic model for the result of analyzing a table schema.

    Attributes:
        step (int): Step number in the workflow.
        action (str): Name of the action performed.
        status (str): 'success' or 'error'.
        database (str): Name of the database analyzed.
        table (Optional[str]): Name of the table analyzed.
        table_schema (Optional[List[Dict[str, Any]]]): List of column definitions for the table.
        columns_count (Optional[int]): Number of columns in the table.
        message (str): Human-friendly status message.
        error (Optional[str]): Error message if status is 'error'.
    """
    step: int = Field(description="Step number")
    action: str = Field(description="Action name")
    status: str = Field(description="'success' or 'error'")
    database: str = Field(description="Database name")
    table: Optional[str] = Field(None, description="Table name analyzed")
    table_schema: Optional[List[Dict[str, Any]]] = Field(None, description="List of column definitions for the table")
    columns_count: Optional[int] = Field(None, description="Number of columns in the table")
    message: str = Field(description="Human-friendly message")
    error: Optional[str] = Field(None, description="Error message when status=='error'")

################################
# Tool Registration
################################

def register_analyze_schema_tools(mcp):
    """
    Register the analyze schema tool with the MCP server.

    This function adds the step3_analyze_schema tool, which analyzes the structure of a given table
    in a PostgreSQL database and returns a structured result.

    Args:
        mcp: The MCP server instance to register tools with.
    """
    @mcp.tool(
        name="step3_analyze_schema",
        description="Analyzes the structure of the selected table",
        tags={"table", "analyse", "schema", "step3", "table_schema"},  # Tags for organization/filtering
        meta={"version": "1.2", "author": "martin"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Step3 Analyse Schema Tool",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=False,  # If true, calling the tool repeatedly with the same arguments will have no additional effect.
            openWorldHint=False,  # If true, this tool may interact with an open world of external entities.
        ),
    )
    async def step3_analyze_schema(ctx: Context, table: str, database: str = POSTGRES_DB) -> AnalyzeSchemaResult:
        """
        Analyze the schema of a specific table in the given database.

        Args:
            ctx (Context): The execution context (provided by MCP framework).
            table (str): The name of the table to analyze.
            database (str, optional): The database name. Defaults to POSTGRES_DB.

        Returns:
            AnalyzeSchemaResult: Structured result containing schema details or error info.
        """
        try:
            await ToolLogger.log_to_client(
                ctx,
                f"Analyzing schema of table '{table}' in database '{database}'...",
                "info"
            )
            # Retrieve schema details for the specified table
            schema = await describe_table(database, table)
            return AnalyzeSchemaResult(
                step=3,
                action="analyze_schema",
                status="success",
                database=database,
                table=table,
                table_schema=schema,
                columns_count=len(schema),
                message=f"✅ Schema analyzed for '{table}': {len(schema)} columns",
                error=None
            )
        except Exception as e:
            # Return error details in the result model
            return AnalyzeSchemaResult(
                step=3,
                action="analyze_schema",
                status="error",
                database=database,
                table=table,
                table_schema=None,
                columns_count=None,
                message=f"❌ Error during schema analysis: {str(e)}",
                error=str(e)
            )

"""
Sample Data Retrieval Tool

This module provides a simple tool to retrieve a small sample of rows from a table
in a PostgreSQL database. It's intended for quick inspection of table contents so
downstream steps or a human operator can better understand the data.

The tool is async and integrates with the MCP (Model Context Protocol) toolset.
"""
from mcp import types
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from helpers.db_helper import execute_safe_query
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
# Helper Functions
################################

async def _sample_data(database: str, table: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch a small sample of rows from a table.

    Args:
        database: Database name to use for the connection.
        table: Name of the table to sample from. Caller should ensure table is a valid identifier.
        limit: Maximum number of rows to return.

    Returns:
        A list of row dictionaries (column -> value). Returns an empty list on error.

    Notes:
        - Table name is interpolated into the SQL statement; this code quotes the
          table identifier to reduce risk, but callers should ensure table names
          are trusted or validated before calling.
        - `execute_safe_query` is expected to return a list of dict-like rows.
    """
    try:
        # NOTE: We double-quote the table name to allow mixed-case or reserved names.
        # This does not fully protect against malicious table names; validate input
        # upstream if needed.
        query = f'SELECT * FROM "{table}" LIMIT {limit};'
        rows = await execute_safe_query(database, query, limit)
        return rows or []
    except Exception as e:
        logger.error(f"Sample error for {table}: {e}")
        return []

class SampleDataResult(BaseModel):
    """
    Pydantic model for results returned by the sample-data tool (step4_get_sample).

    Fields:
        step: Workflow step number.
        action: Action name.
        status: 'success' or 'error'.
        database: Database used.
        table: Table sampled.
        sample_data: Optional list of rows (each row is a dict column->value).
        rows_count: Optional[int] number of rows returned in sample_data.
        message: Human-friendly message describing the outcome.
        error: Optional error string when status == 'error'.
    """
    step: int = Field(description="Step number")
    action: str = Field(description="Action name")
    status: str = Field(description="'success' or 'error'")
    database: str = Field(description="Database name")
    table: Optional[str] = Field(None, description="Table name sampled")
    sample_data: Optional[List[Dict[str, Any]]] = Field(None, description="Rows sampled from the table")
    rows_count: Optional[int] = Field(None, description="Number of rows returned in the sample")
    message: str = Field(description="Human-friendly message")
    error: Optional[str] = Field(None, description="Error message when status=='error'")

################################
# Tool Registration
################################

def register_sample_data_tools(mcp):
    """
    Register the sample-data tool with the MCP server.

    Adds `step4_get_sample` which fetches a small number of rows from the
    specified table and returns a structured `SampleDataResult`.
    """
    @mcp.tool(
        name="step4_get_sample",
        description="Retrieves a data sample to understand the content",
        tags={"table", "analyse", "schema", "step4"},  # Tags for organization/filtering
        meta={"version": "1.2", "author": "martin"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Step4 Get Sample Data",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=False,  # If true, calling the tool repeatedly with the same arguments will have no additional effect.
            openWorldHint=False,  # If true, this tool may interact with an open world of external entities.
        ),
    )
    async def step4_get_sample(table: str, ctx: Context, database: str = POSTGRES_DB) -> SampleDataResult:
        """
        Step 4: Retrieve a small sample of rows from `table` in `database`.

        Returns:
            SampleDataResult: Structured result containing the sample or error details.
        """
        try:
            await ToolLogger.log_to_client(
                ctx,
                f"Retrieving sample data from table '{table}' in database '{database}'...",
                "info"
            )
            # Await the asynchronous sampler to get rows
            sample = await _sample_data(database, table, 3)
            rows_count = len(sample) if sample is not None else 0
            return SampleDataResult(
                step=4,
                action="get_sample",
                status="success",
                database=database,
                table=table,
                sample_data=sample,
                rows_count=rows_count,
                message=f"✅ Sample retrieved: {rows_count} rows from '{table}'",
                error=None,
            )
        except Exception as e:
            # Return a structured error result
            return SampleDataResult(
                step=4,
                action="get_sample",
                status="error",
                database=database,
                table=table,
                sample_data=None,
                rows_count=None,
                message=f"❌ Error during sample retrieval: {str(e)}",
                error=str(e),
            )
"""
Database Table Discovery Tool

This module provides functionality to discover and list tables in a PostgreSQL database.
It includes tools for listing table names, gathering table metadata, and returning results
in a structured format. The module is part of the MCP (Model Context Protocol) toolset
for database introspection.

Key Components:
- Table discovery functionality using PostgreSQL information_schema
- Structured result handling with Pydantic models
- Async-compatible tool registration
- Error handling and logging
"""

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

load_dotenv()
POSTGRES_DB = os.environ.get('POSTGRES_DB')
logger = logging.getLogger(__name__)

################################
# Helper Functions
################################

async def _list_tables(database: str) -> List[str]:
    """
    Internal function to retrieve a list of table names from the specified PostgreSQL database.
    
    Args:
        database (str): The name of the PostgreSQL database to query.
        
    Returns:
        List[str]: A list of table names from the public schema.
        
    Note:
        - Only returns tables from the public schema
        - Excludes views and other non-table objects
        - Returns an empty list if an error occurs
        - Includes table comments from pg_class
    """
    try:
        with get_conn(database) as conn, conn.cursor() as cur:
            cur.execute("""
                    SELECT 
                        t.table_name,
                        obj_description((t.table_schema || '.' || t.table_name)::regclass, 'pg_class') AS table_comment
                    FROM information_schema.tables t
                    WHERE t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                    ORDER BY t.table_name;
            """)
            tables = [row[0] for row in cur.fetchall()]
            logger.info(f"Tables found in {database}: {tables}")
            return tables
    except Exception as e:
        logger.error(f"Table listing error: {e}")
        return []

class DiscoverTablesResult(BaseModel):
    """Structured result for the discover_tables tool."""
    step: int = Field(description="Step number")
    action: str = Field(description="Action name")
    status: str = Field(description="'success' or 'error'")
    database: str = Field(description="Database name")
    tables: List[str] = Field(default_factory=list, description="List of table names")
    count: int = Field(0, description="Number of tables found")
    message: str = Field(description="Human-friendly message")
    error: Optional[str] = Field(None, description="Error message when status=='error'")

################################
# Tool Registration
################################

def register_discover_table_tools(mcp):
    """
    Register all table discovery tools with the MCP server.
    
    This function sets up the table discovery toolset, including:
    - Step 1: Basic table discovery (step1_discover_tables)
    
    Args:
        mcp: The MCP server instance to register tools with.
        
    Note:
        Tools are registered with appropriate metadata, tags, and annotations
        for proper integration with the MCP framework.
    """
    @mcp.tool(
    name="step1_discover_tables",
    description="Discover all tables in the specified PostgreSQL database.",
    tags={"table", "discovery", "step1"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="Step1 Discover Tables Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def step1_discover_tables(ctx: Context, database: str = POSTGRES_DB) -> DiscoverTablesResult:
        """
        Step 1: Discovers and lists all tables in the specified PostgreSQL database.
        
        This async function queries the database to retrieve a list of all tables
        in the public schema. It provides detailed feedback through the MCP context
        and returns a structured result.
        
        Args:
            ctx (Context): The MCP context for logging and client communication
            database (str, optional): The target database name. Defaults to POSTGRES_DB from env.
            
        Returns:
            DiscoverTablesResult: A structured response containing:
                - List of discovered tables
                - Table count
                - Status information
                - Error details (if any)
                
        Note:
            - Only discovers tables in the public schema
            - Excludes views and other database objects
            - Provides real-time feedback through ToolLogger
            - Handles errors gracefully with structured error reporting
        """

        try:
            await ToolLogger.log_to_client(
                ctx,
                f"Discovering tables in database '{database}'...",
                "info"
            )
            tables = await _list_tables(database)
            return DiscoverTablesResult(
                step=1,
                action="discover_tables",
                status="success",
                database=database,
                tables=tables,
                count=len(tables),
                message=f"✅ {len(tables)} table(s) found in '{database}': {', '.join(tables)}",
            )
        except Exception as e:
            return DiscoverTablesResult(
                step=1,
                action="discover_tables",
                status="error",
                database=database,
                tables=[],
                count=0,
                error=str(e),
                message=f"❌ Error during table discovery: {str(e)}",
            )
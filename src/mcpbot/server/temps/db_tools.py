from mcp import types
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from helpers.db_helper import get_conn,execute_safe_query
from helpers.tool_logger import ToolLogger
from fastmcp import Context
from dotenv import load_dotenv
import os
from helpers.prompts import TABLE_SELECTION_PROMPT
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
            logging.info(f"Tables found in {database}: {tables}")
            return tables
    except Exception as e:
        logging.error(f"Table listing error: {e}")
        return []


async def _describe_table(database: str, table: str) -> List[Dict[str, Any]]:
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
        
################################
# Tool Registration
################################

def register_db_tools(mcp):
    """
    Register the db tool with the MCP server.

    """
    @mcp.tool(
    name="list_tables",
    description="Lists tables in a PostgreSQL database.",
    tags={"table", "list"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="List Tables Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def list_tables(database: str, ctx: Context) -> List[str]:
        """Lists tables in a database"""
        return _list_tables(database, ctx)

    @mcp.tool(
    name="describe_table",
    description="Describes the schema of a table in a PostgreSQL database.",
    tags={"table", "describe", "schema"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="Describe Tables Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def describe_table(database: str, table: str) -> List[Dict[str, Any]]:
        """Describes the schema of a table"""
        return await _describe_table(database, table)


    @mcp.tool(
    name="run_sql",
    description="Executes a safe SQL SELECT query",
    tags={"execute", "sql"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="Run SQL Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def run_sql(database: str, query: str) -> List[Dict[str, Any]]:
        """Executes a safe SQL SELECT query"""
        logger.info(f"SQL execution on {database}: {query}")
        return await execute_safe_query(database, query)


    @mcp.tool(
    name="sample_data",
    description="Displays a sample of data from a table",
    tags={"table", "sample"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="Sample Data Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def sample_data(database: str, table: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Displays a sample of data from a table"""
        return await _sample_data(database, table, limit)
"""
Generate Smart SQL Tool

This module generates an intelligent SQL query based on a user question, the
table schema, and sample data. The core function delegates to an LLM helper
(_generate_sql_query) to construct a context-aware SQL statement. The tool
returns a structured Pydantic result for predictable downstream handling.
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
import json

################################
# Configuration and Initialization
################################


load_dotenv()  # Load environment variables from .env file
POSTGRES_DB = os.environ.get('POSTGRES_DB')  # Default database name from environment
logger = logging.getLogger(__name__)  # Module-level logger

SQL_GENERATION_PROMPT = """You are a PostgreSQL expert SQL writer. Your task is to generate a precise and efficient SQL query to answer the user's question based on the provided context.

<context>
User Question: "{question}"
Database: {database}
Table: {table}
Schema: {table_schema}
Sample Data: {sample_data}
</context>

<instructions>
1.  **Analyze the Goal**: Understand the user's core question. Are they asking for a list, a count, an average, or a comparison?
2.  **Column Selection**: Select specific columns that directly answer the question. Avoid `SELECT *` unless absolutely necessary. Use aliases for clarity if needed.
3.  **Filtering (WHERE clause)**: Apply filters based on the conditions in the question (e.g., `status = 'active'`, `salary > 50000`). Use `ILIKE` for case-insensitive text searches.
4.  **Complex Logic**:
    *   **Aggregations**: If the question involves calculations like average, sum, or count for groups, use `GROUP BY` with functions like `AVG()`, `SUM()`, `COUNT()`.
    *   **Subqueries/CTEs**: For questions involving comparisons against a calculated value (e.g., "salary below the department average"), you MUST use a subquery or a Common Table Expression (CTE).
    *   *Example for "salary below department average"*: You need to first calculate the average salary for each department in a subquery, then join it back to the main table to filter employees.
5.  **Performance**: Add a `LIMIT` clause (e.g., `LIMIT 100`) to prevent excessively large results, unless the user asks for a full count or a specific number.
6.  **Final Review**: Ensure the query is syntactically correct for PostgreSQL and uses the exact column names from the provided schema.
</instructions>

<constraints>
- ONLY generate SELECT statements. No DML/DDL (INSERT, UPDATE, DROP, etc.).
- The query must be a single, executable statement.
</constraints>

<output_format>
Return ONLY the raw SQL query, without any surrounding text, comments, or markdown backticks.
</output_format>"""

################################
# Helper Functions
################################


async def _generate_sql_query(user_question: str,
                              database: str,
                              table: str,
                              table_schema: List[Dict],
                              sample_data: List[Dict],
                              ctx: Context) -> str:
    """
    Generate an SQL query using the available context and an LLM.

    The function fills a prompt template with the user question, database
    and table context, table schema, and sample rows. It then requests a
    response from the MCP-provided context (`ctx.sample`) which is expected to
    run the configured LLM. The returned text is cleaned and returned as a
    SQL statement (trailing semicolons removed).

    If any error occurs (missing model, LLM error, etc.) this function
    falls back to a safe default SELECT that returns a small number of rows
    from the target table.

    Args:
        user_question: Natural language question from the user.
        database: Database name used to provide context.
        table: Table name to target with the SQL.
        table_schema: List of column metadata dicts describing the table.
        sample_data: Sample rows from the table to help the LLM understand data values.
        ctx: MCP execution context; used to call `ctx.sample(prompt)`.

    Returns:
        A SQL string (without trailing semicolon). On error returns a safe
        `SELECT * FROM "table" LIMIT 10` statement.
    """
    try:
        filled_prompt = SQL_GENERATION_PROMPT.format(
            question=user_question,
            database=database,
            table=table,
            table_schema=json.dumps(table_schema, indent=2),
            sample_data=json.dumps(sample_data, indent=2, ensure_ascii=False),
        )

        # Request LLM analysis via MCP context. ctx.sample should return a
        # string-like response containing SQL. Using MCP's context keeps this
        # module decoupled from the concrete LLM implementation.
        response = await ctx.sample(filled_prompt)
        sql = response.text.strip().lower()
        # Strip common code fences and trailing semicolon; return cleaned SQL.
        sql = sql.replace("```sql", "").replace("```", "").strip().rstrip(";")
        logger.info(f"SQL query generated: {sql}")
        return sql
    except Exception as e:
        # Log and fall back to a safe, simple SELECT. This ensures downstream
        # steps still receive a usable SQL string even if generation fails.
        logger.error(f"SQL generation error: {e}")
        return f'SELECT * FROM "{table}" LIMIT 10;'


class GenerateSqlResult(BaseModel):
    """
    Result model for SQL generation (step5_generate_sql).

    Fields:
        step: Workflow step number (5).
        action: Action name ('generate_sql').
        status: 'success' or 'error'.
        user_question: The original user question that drove SQL generation.
        database: Database used for context.
        table: Table the SQL targets.
        sql_query: The generated SQL statement (string) or None on error.
        message: Human-readable summary message.
        error: Optional error string when status == 'error'.
    """
    step: int = Field(description="Step number")
    action: str = Field(description="Action name")
    status: str = Field(description="'success' or 'error'")
    user_question: Optional[str] = Field(None, description="Original user question")
    database: str = Field(description="Database name")
    table: Optional[str] = Field(None, description="Table name targeted by the SQL")
    sql_query: Optional[str] = Field(None, description="Generated SQL query")
    message: str = Field(description="Human-friendly message")
    error: Optional[str] = Field(None, description="Error message when status=='error'")


################################
# Tool Registration
################################
def register_generate_sql_tools(mcp):
    """
    Register the generate_sql tool with the MCP server.
    """
    @mcp.tool(
        name="step5_generate_sql",
        description="Generates an intelligent SQL query based on user question, table schema, and sample data.",
        tags={"table", "generate", "sql", "step5"},  # Tags for organization/filtering
        meta={"version": "1.2", "author": "martin"},  # Custom metadata
        annotations=types.ToolAnnotations(
            title="Step5 Generate SQL Tool",
            readOnlyHint=True,  # If true, the tool does not modify its environment.
            destructiveHint=False,  # If true, the tool may perform destructive updates to its environment.
            idempotentHint=False,  # If true, calling the tool repeatedly with the same arguments will have no additional effect.
            openWorldHint=False,  # If true, this tool may interact with an open world of external entities.
        ),
    )
    async def step5_generate_sql(user_question: str, table: str,
                        table_schema: List[Dict], sample_data_list: List[Dict], ctx: Context, database:str = POSTGRES_DB ) -> GenerateSqlResult:
        """
        Step 5: Generate an SQL query for the given question and table.

        Logs progress to the MCP client, invokes the internal LLM-backed helper to
        generate a SQL string, and returns a `GenerateSqlResult` containing the
        SQL or error information.
        """
        try:
            await ToolLogger.log_to_client(
                ctx,
                f"Generating SQL query in database '{database}'...",
                "info",
            )

            # Generate the SQL (may use an LLM internally). Use explicit keyword
            # arguments to avoid accidental positional mismatches between
            # database and table parameters.
            sql_query = await _generate_sql_query(
                user_question=user_question,
                database=database,
                table=table,
                table_schema=table_schema,
                sample_data=sample_data_list,
                ctx=ctx,
            )
            logger.info(f"Generated SQL: {sql_query}")
            short_sql = (sql_query[:50] + "...") if sql_query and len(sql_query) > 50 else (sql_query or "")
            await ToolLogger.log_to_client(
                ctx,
                f"Generating SQL query '{short_sql}'...",
                "info",
            )
            return GenerateSqlResult(
                step=5,
                action="generate_sql",
                status="success",
                user_question=user_question,
                database=database,
                table=table,
                sql_query=sql_query,
                message=f"✅ SQL query generated: {short_sql}",
                error=None,
            )
        except Exception as e:
            return GenerateSqlResult(
                step=5,
                action="generate_sql",
                status="error",
                user_question=user_question,
                database=database,
                table=table,
                sql_query=None,
                message=f"❌ Error during SQL generation: {str(e)}",
                error=str(e),
            )
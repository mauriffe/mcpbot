from mcp import types
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from helpers.db_helper import execute_safe_query
from helpers.tool_logger import ToolLogger
from fastmcp import Context
from dotenv import load_dotenv
import os
from helpers.prompts import ERROR_RECOVERY_PROMPT
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

async def _generate_corrected_sql(user_question: str, database: str, table: str,
                           table_schema: List[Dict], sample_data: List[Dict],
                           failed_sql: str, error: str, ctx: Context) -> str:
    """Generates a corrected SQL query after an error."""
    try:
        filled_prompt = ERROR_RECOVERY_PROMPT.format(
            question=user_question,
            database=database,
            table=table,
            failed_sql=failed_sql,
            error=error,
            table_schema=json.dumps(table_schema, indent=2),
            sample_data=json.dumps(sample_data, indent=2, ensure_ascii=False)
        )

        # Request LLM analysis
        response = await ctx.sample(filled_prompt)
        sql = response.text.strip().lower()
        sql = sql.replace("```sql", "").replace("```", "").strip().rstrip(";")
        logger.info(f"Corrected SQL query: {sql}")
        return sql
    except Exception as e:
        logger.error(f"SQL correction error: {e}")
        return f'SELECT * FROM "{table}" LIMIT 10;'
    

class ExecuteQueryResult(BaseModel):
    """
    Standardized result object for query execution (step6_execute_query).

    This Pydantic model provides a consistent shape for success, retry-success,
    and error responses from the execution tool. Downstream consumers should
    rely on this model instead of ad-hoc dicts.
    """
    step: int = Field(description="Workflow step number")
    action: str = Field(description="Action name")
    status: str = Field(description="'success', 'success_after_retry' or 'error'")
    database: str = Field(description="Database name")
    sql_query: Optional[str] = Field(None, description="SQL that was executed (original or final)")
    original_sql: Optional[str] = Field(None, description="Original SQL attempted (when retry was used)")
    corrected_sql: Optional[str] = Field(None, description="Corrected SQL used after retry")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Rows returned by the query")
    rows_count: int = Field(0, description="Number of rows returned")
    message: str = Field(description="Human-friendly message")
    error: Optional[str] = Field(None, description="Error message when status=='error'")


################################
# Tool Registration
################################

def register_execute_query_tools(mcp):
    """
    Register the execute_query tool with the MCP server.

    """
    @mcp.tool(
    name="step6_execute_query",
    description="Step 6: Executes the SQL query with error handling",
    tags={"table", "execute", "sql", "step6"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "martin"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="Step6 Execute Query Tool",
                readOnlyHint=True, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    async def step6_execute_query(sql_query: str, ctx: Context, user_question: str = "",
                            table: str = "",table_schema: List[Dict] = None,
                            sample_data_list: List[Dict] = None, database: str = POSTGRES_DB) -> ExecuteQueryResult:
        """
        Step 6: Execute the provided SQL query against the database.

        The function attempts to run `sql_query` using `execute_safe_query`. If
        execution fails and sufficient context is provided (user_question,
        table, schema, sample_data_list), it will request a corrected SQL from
        the LLM and retry the execution. Results are returned as an
        `ExecuteQueryResult` model for consistent downstream consumption.
        """
        max_retries = 3
        attempt = 0
        current_sql = sql_query
        original_sql = sql_query
        corrected_sql = None
        last_error = None
        await ToolLogger.log_to_client(
            ctx,
            f"Executing SQL query in database '{database}'...",
            "info"
        )
        while attempt <= max_retries:
            try:
                results = await execute_safe_query(database, current_sql)
                rows_count = len(results) if results is not None else 0
                status = "success" if attempt == 0 else "success_after_retry"
                return ExecuteQueryResult(
                    step=6,
                    action="execute_query",
                    status=status,
                    database=database,
                    sql_query=current_sql,
                    original_sql=original_sql if attempt > 0 else None,
                    corrected_sql=corrected_sql,
                    results=results or [],
                    rows_count=rows_count,
                    message=f"✅ Query executed successfully: {rows_count} result(s)" if attempt == 0 else f"✅ Query corrected and executed: {rows_count} result(s)",
                    error=None,
                )
            except Exception as e:
                last_error = str(e)
                if user_question and table and table_schema and sample_data_list:
                    logger.info(f"🔄 Attempting to correct the query after error: {e}")
                    corrected_sql = await _generate_corrected_sql(
                        user_question, database, table, table_schema, sample_data_list, current_sql, last_error, ctx
                    )
                    current_sql = corrected_sql
                    attempt += 1
                else:
                    break
        # If all attempts fail, return error result
        return ExecuteQueryResult(
            step=6,
            action="execute_query",
            status="error",
            database=database,
            sql_query=current_sql,
            original_sql=original_sql if attempt > 0 else None,
            corrected_sql=corrected_sql,
            results=[],
            rows_count=0,
            message=f"❌ Error during execution: {last_error}",
            error=last_error,
        )

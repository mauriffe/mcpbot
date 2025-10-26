from mcp import types
from pydantic import BaseModel, Field

class AdditionArgs(BaseModel):
    """Arguments for the addition tool."""
    a: float = Field(description="First number to add")
    b: float = Field(description="Second number to add")

def register_calcul_tools(mcp):
    """Register all math-related tools."""

    @mcp.tool(
    name="addition",
    description="Adds two integer numbers together.", # Custom description
    tags={"sensitive", "calculation", "maths"},      # Optional tags for organization/filtering
    meta={"version": "1.2", "author": "support-team"},  # Custom metadata
    annotations=types.ToolAnnotations(
                title="The additive tool",
                readOnlyHint=False, #If true, the tool does not modify its environment.
                destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                idempotentHint=False, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
            )
    )
    def handle_addition(arguments: dict) -> list[types.TextContent]:
        """Handle the addition tool call."""
        # Validate and parse arguments
        args = AdditionArgs(**arguments)

        # Perform the addition
        result = args.a + args.b

        # Return the result
        return [
            types.TextContent(
                type="text",
                text=f"The sum of {args.a} and {args.b} is {result}"
            )
        ]
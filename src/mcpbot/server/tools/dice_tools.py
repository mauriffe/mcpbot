from mcp import types
from fastmcp import Context
import random
from enum import Enum

class UserAcceptance(Enum):
    YES = "yes"
    Y = "y"

def register_dice_tools(mcp):
    @mcp.tool(
        name="roll_dice",
        description="Throw dices and returns the roll.", # Custom description
        tags={"sensitive", "dice"},      # Optional tags for organization/filtering
        meta={"version": "1.2", "author": "support-team"},  # Custom metadata
        annotations=types.ToolAnnotations(
                    title="The Dice Roller",
                    readOnlyHint=True, #If true, the tool does not modify its environment.
                    destructiveHint=False, #If true, the tool may perform destructive updates to its environment.
                    idempotentHint=True, #If true, calling the tool repeatedly with the same arguments will have no additional effect on the environment.
                    openWorldHint=False, #If true, this tool may interact with an “open world” of external entities. If false, the tool’s domain of interaction is closed.
                )
    )
    async def roll_dice(n_dice: int, ctx: Context) -> dict:
        """Roll `n_dice` 6-sided dice and return the results."""
        try:
            print(f"[DICE] 🎲 Starting roll for {n_dice} dice")
            print(f"[DICE] Calling ctx.elicit()...")

            result = await ctx.elicit(
                f"Do you want to roll {n_dice} dice? (yes/y to confirm)",
                response_type=UserAcceptance
            )

            print(f"[DICE] ✅ Elicitation completed!")
            print(f"[DICE] Result type: {type(result)}")
            print(f"[DICE] Result value: {result}")
            print(f"[DICE] Result repr: {repr(result)}")
            print(f"[DICE] Has 'action' attr: {hasattr(result, 'action')}")

            if hasattr(result, 'action'):
                print(f"[DICE] Result.action = {result.action}")

            if hasattr(result, 'value'):
                print(f"[DICE] Result.value = {result.value}")

            # Check different ways the result might indicate acceptance
            accepted = False

            if hasattr(result, 'action') and result.action == "accept":
                accepted = True
                print("[DICE] ✅ Accepted via result.action")
            elif isinstance(result, UserAcceptance):
                accepted = True
                print("[DICE] ✅ Accepted via UserAcceptance enum instance")
            elif isinstance(result, dict) and result.get('action') == 'accept':
                accepted = True
                print("[DICE] ✅ Accepted via dict action")
            elif str(result).lower() in ['yes', 'y']:
                accepted = True
                print("[DICE] ✅ Accepted via string value")

            if accepted:
                rolls = [random.randint(1, 6) for _ in range(n_dice)]
                print(f"[DICE] 🎲 Rolled: {rolls}")
                return {
                    "success": True,
                    "rolls": rolls,
                    "total": sum(rolls),
                    "message": f"Rolled {n_dice} dice: {rolls}. Total: {sum(rolls)}"
                }
            else:
                print("[DICE] ❌ User declined")
                return {
                    "success": False,
                    "message": "Dice roll cancelled by user"
                }

        except Exception as e:
            print(f"[DICE] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to roll dice: {str(e)}"
            }
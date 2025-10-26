from mcp import types
from fastmcp import Context
import random
from enum import Enum
import string
import logging

logger = logging.getLogger(__name__)

# --- Value Generation ---
def generate_random_string(length=5):
    """Generates a random string of a given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Generate the random string
RANDOM_YES_VALUE = generate_random_string(length=8) # e.g., 'aBcDeF'

logger.info(f"Assigning 'YES' to: {RANDOM_YES_VALUE}")

# --- Enum Definition ---
class UserAcceptance(Enum):
    # Assign the generated values to the enum members
    YES = RANDOM_YES_VALUE

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
            logger.info(f"[DICE] 🎲 Starting roll for {n_dice} dice")
            logger.info(f"[DICE] Calling ctx.elicit()...")

            result = await ctx.elicit(
                f"Do you want to roll {n_dice} dice? (Type {RANDOM_YES_VALUE} to confirm)",
                response_type=UserAcceptance
            )

            logger.info(f"[DICE] ✅ Elicitation completed!")
            logger.info(f"[DICE] Result type: {type(result)}")
            logger.info(f"[DICE] Result value: {result}")
            logger.info(f"[DICE] Result repr: {repr(result)}")
            logger.info(f"[DICE] Has 'action' attr: {hasattr(result, 'action')}")

            if hasattr(result, 'action'):
                logger.info(f"[DICE] Result.action = {result.action}")

            if hasattr(result, 'value'):
                logger.info(f"[DICE] Result.value = {result.value}")

            # Check different ways the result might indicate acceptance
            accepted = False

            if hasattr(result, 'action') and result.action == "accept":
                accepted = True
                logger.info("[DICE] ✅ Accepted via result.action")

            if accepted:
                rolls = [random.randint(1, 6) for _ in range(n_dice)]
                logger.info(f"[DICE] 🎲 Rolled: {rolls}")
                return {
                    "success": True,
                    "rolls": rolls,
                    "total": sum(rolls),
                    "message": f"Rolled {n_dice} dice: {rolls}. Total: {sum(rolls)}"
                }
            else:
                logger.info("[DICE] ❌ User declined")
                return {
                    "success": False,
                    "message": "Dice roll cancelled by user"
                }

        except Exception as e:
            logger.exception(f"[DICE] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to roll dice: {str(e)}"
            }
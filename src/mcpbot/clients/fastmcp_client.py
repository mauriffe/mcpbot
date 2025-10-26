import asyncio
from fastmcp import Client
import os
import logging
from fastmcp.client.logging import LogMessage
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext
from datetime import datetime

os.makedirs("logs", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join("logs", f"mcpclient_log_{timestamp}.log")
# Get a logger for the module where the client is used
logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers = [
                logging.FileHandler(log_filename),
            ]
        )

async def detailed_log_handler(message: LogMessage):
    msg = message.data.get('msg')
    extra = message.data.get('extra', 'No extra data')

    if message.level == "error":
        logging.error(f"ERROR: {msg} | Details: {extra}")
    elif message.level == "warning":
        logging.warning(f"WARNING: {msg} | Details: {extra}")
    else:
        logging.info(f"{message.level.upper()}: {msg} | Details: {extra}")


async def elicitation_handler(message: str, response_type: type, params, context):
    # Present the message to the user and collect input
    print(f"Server asks: {message}")
    user_response = input("Your response: ")

    # Create response using the provided dataclass type
    # FastMCP converted the JSON schema to this Python type for you
    response_data = response_type(value=user_response)

    if not user_response:
        # For non-acceptance, use ElicitResult explicitly
        return ElicitResult(action="decline")

    # You can return data directly - FastMCP will implicitly accept the elicitation
    return response_data

    # Or explicitly return an ElicitResult for more control
    # action: Literal['accept', 'decline', 'cancel']
    # content: The user’s input data (required for “accept”, omitted for “decline”/“cancel”)
    # return ElicitResult(action="accept", content=response_data)

async def basic_sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    context: RequestContext
) -> str:
    # Extract message content
    conversation = []
    for message in messages:
        content = message.content.text if hasattr(message.content, 'text') else str(message.content)
        conversation.append(f"{message.role}: {content}")

    # Use the system prompt if provided
    system_prompt = params.systemPrompt or "You are a helpful assistant."

    # Here you would integrate with your preferred LLM service
    # This is just a placeholder response
    return f"Response based on conversation: {' | '.join(conversation)}"


# HTTP server
client = Client(
    "http://127.0.0.1:8000/mcp",
    log_handler=detailed_log_handler,
    elicitation_handler=elicitation_handler,
    sampling_handler=basic_sampling_handler
)

async def main():
    async with client:
        # Basic server interaction
        await client.ping()

        # List available operations
        logging.info("Connected to MCP Server running with the following components...")
        logging.info(f"Tools: {list(await client.list_tools())}")
        logging.info(f"Resources: {list(await client.list_resources())}")
        logging.info(f"Prompts: {list(await client.list_prompts())}")

        # Execute operations
        result = await client.call_tool("Roll Dice", {"n_dice": 3})
        logging.info(result)
        result = await client.call_tool("Addition", {"arguments": {"a": 3, "b": 4}})
        logging.info(result)
        result = await client.call_tool("Get Weather", {"cities":['Paris','London']})
        logging.info(result)

asyncio.run(main())
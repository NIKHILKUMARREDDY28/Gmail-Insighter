import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, SseMcpToolAdapter, mcp_server_tools

from settings import settings


async def main() -> None:
    # Create server params for the remote MCP service
    server_params = SseServerParams(
        url="http://127.0.0.1:8000/sse",
        headers={ "Content-Type": "application/json"},
        timeout=30,  # Connection timeout in seconds
    )

    tools = await mcp_server_tools(server_params)

    # Get the translation tool from the server
    # adapter = await SseMcpToolAdapter.from_server_params(server_params, "get_mails")

    # Create an agent that can use the translation tool
    model_client = OpenAIChatCompletionClient(model="gpt-4", api_key=settings.OPENAI_API_KEY)
    agent = AssistantAgent(
        name="translator",
        model_client=model_client,
        tools=tools,
        system_message="You are a world class email summariser. You can summarise emails using the get_mails tool.",
    )

    # Let the agent translate some text
    await Console(
        agent.run_stream(task="Get the subjects in my mails", cancellation_token=CancellationToken())
    )


if __name__ == "__main__":
    asyncio.run(main())
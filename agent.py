# agent.py

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from settings import settings

async def main() -> None:
    server_params = SseServerParams(
        url="http://127.0.0.1:8000/sse",
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    tools = await mcp_server_tools(server_params)

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=settings.OPENAI_API_KEY,
    )

    agent = AssistantAgent(
        name="email_summarizer",
        model_client=model_client,
        tools=tools,
        system_message=(
            "You are a world-class email summariser. "
            "Use the `get_mails` tool by passing the access_token, query, and max_results. "
            "Return a bulleted list of the email subjects."
        ),
    )

    # For console testing:
    await Console(
        agent.run_stream(
            task="Fetch the 5 most recent emails with query 'subject:Demo'",
            cancellation_token=CancellationToken()
        )
    )

if __name__ == "__main__":
    asyncio.run(main())

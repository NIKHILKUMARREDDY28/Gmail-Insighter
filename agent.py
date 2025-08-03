# agent.py

import asyncio
import logging

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from settings import settings


logging.debug("MCP Server Configuration:")
logging.debug(f"  URL: {settings.MCP_SERVER_URL}")
mcp_server_params = SseServerParams(
    url=settings.MCP_SERVER_URL,
    headers={"Content-Type": "application/json"},
    timeout=30
)

mcp_tools = mcp_server_tools(mcp_server_params)


openai_client =  OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=settings.OPENAI_API_KEY
)

async def get_emails_using_mcp(access_token: str, query: str) -> str:

    tools = await mcp_tools
    print(tools)
    email_retriever_agent = AssistantAgent(
        name="email_retriever",
        model_client=openai_client,
        tools=tools,
        system_message=
            "You are a world-class email summarizer. "
            "You will be provided with tools to fetch and summarize emails. "
            f"Use the provided access token: {access_token} to access tools for authentication. "
            "Your task is to fetch the most recent emails based on the query provided.",

    )


    result = await email_retriever_agent.run(
        task=query,
        cancellation_token=CancellationToken()
    )
    return result



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    print("Starting MCP Email Retrieval Agent...")

    access_token = "your_access_token_here"  # Replace with your actual access token
    query = "Get my"
    print(f"Using access token: {access_token}")
    print(f"Querying emails with query: {query}")
    import asyncio
    result = asyncio.run(get_emails_using_mcp(access_token, query))
    print("Email retrieval completed.")
    print("Result:", result)




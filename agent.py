# agent.py

import asyncio
import logging

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, FunctionCallTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools

from settings import settings
from config import EMAIL_RETRIEVER_AGENT_SYSTEM_PROMPT, EMAIL_CRITIC_AGENT_SYSTEM_PROMPT, response_dispatcher

logging.debug("MCP Server Configuration:")
logging.debug(f"  URL: {settings.MCP_SERVER_URL}")
mcp_server_params = SseServerParams(
    url=settings.MCP_SERVER_URL,
    headers={"Content-Type": "application/json"},
    timeout=30
)

mcp_tools = mcp_server_tools(mcp_server_params)

tools = asyncio.run(mcp_tools)

openai_client =  OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=settings.OPENAI_API_KEY
)


function_call_termination = FunctionCallTermination(function_name="response_dispatcher")


async def get_emails_using_mcp(access_token: str, query: str) -> str:


    email_retriever_agent = AssistantAgent(
        name="email_retriever",
        model_client=openai_client,
        tools=tools,
        system_message=EMAIL_RETRIEVER_AGENT_SYSTEM_PROMPT.format(access_token=access_token)
    )

    critic_agent = AssistantAgent(
        name="critic_agent",
        description="A critic agent that evaluates the response of the email retriever agent.",
        model_client=openai_client,
        tools=[response_dispatcher],
        system_message=EMAIL_CRITIC_AGENT_SYSTEM_PROMPT,
    )

    # Create a console for interaction
    agents = [email_retriever_agent, critic_agent]

    research_helper_team = RoundRobinGroupChat(
        agents,
        max_turns=10,
        termination_condition=TextMentionTermination("TERMINATE") | function_call_termination
    )

    response = await research_helper_team.run(task=query)
    logging.debug("Response from research helper team:")

    messages = response.messages

    for agent in messages:
        logging.debug(f"{agent.source}: {agent}")
    # Extract the final response from the email retriever agent
    return messages





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




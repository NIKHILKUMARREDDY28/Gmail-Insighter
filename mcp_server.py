# mcp_server.py

from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import build_resource_service

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool
async def get_mails(access_token: str, query: str, max_results: int = 5) -> dict:
    """Fetch up to `max_results` emails matching `query`."""
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    credentials = Credentials(token=access_token, scopes=SCOPES)
    api_resource = build_resource_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    search_tool = toolkit.get_search_tool()
    search_results = await search_tool.arun({
        "query": query,
        "max_results": max_results
    })
    if not search_results:
        return {"error": "No emails found"}
    return search_results

if __name__ == "__main__":
    mcp.run(transport="sse")

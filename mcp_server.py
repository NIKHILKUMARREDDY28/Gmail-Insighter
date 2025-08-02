from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from langchain_google_community.gmail.search import GmailSearch
from googleapiclient.discovery import build
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# sample_email_data = {
#     "mails": [
#         {
#             "id": "1",
#             "subject": "Welcome to MCP",
#             "sender": "test@test.com",
#             "body": "This is a sample email body.",
#             "timestamp": "2023-10-01T12:00:00Z"
#         },
#         {
#             "id": "2",
#             "subject": "Your MCP account",
#             "sender": "test2@test.com",
#             "body": "This is another sample email body.",
#             "timestamp": "2023-10-02T12:00:00Z"
#         }
#     ]
# }


@mcp.tool
async def get_mails(access_token: str, query: str, max_results: str = 5) -> dict:
    # This is a placeholder for the actual mail retrieval logic
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]  # or "https://mail.google.com/"

    credentials = Credentials(
        token=access_token,
        scopes=SCOPES
        # If you also have a refresh_token, client_id, client_secret and token_uri,
        # you can include them here so the token auto‑refreshes.
    )
    api_resource = build_resource_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    search_tool = toolkit.get_search_tool()
    search_results = await search_tool.arun({"query": query, "max_results": max_results})
    if not search_results:
        return {"error": "No emails found"}
    # For demonstration, we return a static sample email data
    return search_results


if __name__ == "__main__":
    mcp.run(transport="sse")
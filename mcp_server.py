import traceback

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from langchain_google_community.gmail.search import GmailSearch, Resource

from logger.app_logger import log_message

from fastmcp import FastMCP

from cache import get_session_details_from_cache

from langchain_community.tools.gmail.search import GmailSearch

mcp = FastMCP("Demo 🚀")


@mcp.tool
async def get_top_mails_for_query(session_id: str, query: str, top_n_mails: int = 10) -> dict:
    """Gets the top N emails for a given query using the Gmail API.

    :param session_id: User Session identifier.
    :param query: Refined search query to find emails.
    :param top_n_mails: Number of top emails to retrieve.

    """
    try:

        session_data = get_session_details_from_cache(session_id)

        if not session_data:
            log_message(f"[{session_id}]: No session data found for session_id: {session_id}", level="warning")
            raise ValueError(f"No session data found for session_id: {session_id}")

        access_token = session_data.get("access_token")
        refresh_token = session_data.get("refresh_token")
        scopes = session_data.get("scope")
        id_token = session_data.get("id_token")

        credentials = Credentials(token=access_token, id_token=id_token, refresh_token=refresh_token, scopes=scopes)
        # Build the Gmail API client.
        api_resource = build("gmail", "v1", credentials=credentials)

        # Initialise the GmailSearch tool.
        gmail_search = GmailSearch(api_resource=api_resource)

        # Build the search input as a dict that matches the schema.
        search_input = {
            "query": query,
            "resource": Resource.MESSAGES,  # or Resource.THREADS
            "max_results": top_n_mails
        }

        results = await gmail_search.ainvoke(search_input)
        if not results:
            log_message(f"[{session_id}]: No emails found for query: {query}", level="info")
            return {
                "success": True,
                "count": 0,
                "emails": []
            }
        return {
            "success": True,
            "count": len(results),
            "emails": results
        }

    except Exception as e:
        log_message(f"[{session_id}]: Error retrieving emails: {traceback.format_exc()}", level="error")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport="sse")

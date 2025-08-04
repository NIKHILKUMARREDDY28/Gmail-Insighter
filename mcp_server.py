
import logging
import traceback

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from langchain_google_community.gmail.search import GmailSearch, Resource

logging.basicConfig(level=logging.DEBUG)

from fastmcp import FastMCP


from langchain_community.tools.gmail.search import GmailSearch

mcp = FastMCP("Demo 🚀")


@mcp.tool
async def get_top_mails_for_query(access_token: str, query: str, top_n_mails: int = 10) -> dict:
    """Gets the top N emails for a given query using the Gmail API.

    :param access_token: OAuth2 access token for Gmail API.
    :param query: Refined search query to find emails.
    :param top_n_mails: Number of top emails to retrieve.

    """
    try:
        # Build credentials from the OAuth access token.
        scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
        credentials = Credentials(token=access_token, scopes=scopes)

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

        logging.debug(results)
        return {
            "success": True,
            "count": len(results),
            "emails": results
        }

    except Exception as e:
        logging.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }



if __name__ == "__main__":
    mcp.run(transport="sse")

# ──────── Configuration ────────────────────────────────────────────────────
import logging
import os


from requests_oauthlib import OAuth2Session
import streamlit as st

from settings import settings

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL             = "https://oauth2.googleapis.com/token"
SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]
logging.debug("Initializing Google OAuth with:")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID",     "") or settings.GOOGLE_CLIENT_ID
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "") or settings.GOOGLE_CLIENT_SECRET

EMAIL_RETRIEVER_AGENT_SYSTEM_PROMPT = """
You are an email retriever agent. Your task is to retrieve emails based on user queries.
You will be provide with the tools and authenticated session_id : {access_token} to interact with the users mails.Think step by step and formulate a better query to retrieve the emails.
You are allowed to use the same tools multiple times to refine your query and get the best results.
Once You are confident about the retrieved emails, You can respond the user with the structured response.
Generalise the query to retrieve the emails, but do not use any personal information of the user.
"""

EMAIL_CRITIC_AGENT_SYSTEM_PROMPT = """
You are a critic agent. You will be evaluating the response of the email retriever agent.
Once you are satisfied with the response, you can respond with 'TERMINATE' to end the conversation.
Collect the Structured response from the email retriever agent and return it to the user using the `response_dispatcher` function.
If the response is not satisfactory, you can ask the email retriever agent to refine the query
and get better results. You can also ask the user for more information if needed.
"""


def response_dispatcher(response: str, is_final: bool = False) -> str:
   """
   This function collects the final response from the critic agent and returns it to the user in a structured format.

    :param response: The final response for the user.
    :param is_final: Whether this is the final response or not.
   """
   return None



# ──────── OAuth Client ─────────────────────────────────────────────────────
class GoogleOAuth:
    def __init__(self):
        self.oauth = OAuth2Session(
            CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
        )

    def get_authorization_url(self) -> str:
        auth_url, state = self.oauth.authorization_url(
            AUTHORIZATION_BASE_URL,
            access_type="offline",
            prompt="consent"
        )
        st.session_state["oauth_state"] = state
        return auth_url

    def fetch_token(self, code: str) -> dict:
        oauth = OAuth2Session(
            CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            state=st.session_state.get("oauth_state"),
            scope=SCOPE,
        )
        return oauth.fetch_token(
            TOKEN_URL,
            code=code,
            client_secret=CLIENT_SECRET,
            include_client_id=True,
        )

    def save_token(self, token: dict):
        st.session_state["token_data"] = token

    def get_saved_token(self) -> dict:
        return st.session_state.get("token_data")

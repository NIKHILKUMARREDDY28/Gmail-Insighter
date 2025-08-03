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

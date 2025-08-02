import os
import asyncio
import streamlit as st
from requests_oauthlib import OAuth2Session
from dataclasses import dataclass, field

from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from settings import settings

# ──────── Configuration ────────────────────────────────────────────────────
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL             = "https://oauth2.googleapis.com/token"
SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
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


# ──────── Email Summariser Pipeline ─────────────────────────────────────────
@dataclass
class EmailSummarizerPipeline:
    access_token: str
    model_name: str = "gpt-4"
    api_key:    str  = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    sse_url:    str  = "http://127.0.0.1:8000/sse"

    async def _build_tools(self):
        params = SseServerParams(
            url=self.sse_url,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        return await mcp_server_tools(params)

    async def _make_agent(self, tools):
        client = OpenAIChatCompletionClient(model=self.model_name, api_key=self.api_key)
        return AssistantAgent(
            name="email_summarizer",
            model_client=client,
            tools=tools,
            system_message=(
                "You are a world-class email summariser. "
                "Use the `get_mails` tool with the provided access_token, query, and max_results. "
                "Return a bulleted list of the email subjects."
            ),
        )

    async def summarize(self, query: str, max_results: int) -> str:
        tools = await self._build_tools()
        agent = await self._make_agent(tools)
        prompt = (
            f"Fetch the {max_results} most recent emails matching this query: '{query}'. "
            f"Use this access token: {self.access_token}"
        )
        return await agent.run(task=prompt, cancellation_token=CancellationToken())


# ──────── Streamlit App ────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Google OAuth Email Summariser", page_icon="✉️")
    st.title("Email Summariser Pipeline")

    # Ensure credentials are set
    if not CLIENT_ID or not CLIENT_SECRET:
        st.error("🔐 Missing GOOGLE_CLIENT_ID / SECRET. Please set them and restart.")
        return

    oauth = GoogleOAuth()

    # 1) Check for existing token in session
    token = oauth.get_saved_token()
    code  = st.experimental_get_query_params().get("code", [None])[0]

    # 2) If no token and no code, show login
    if token is None and code is None:
        st.write("Click below to sign in with Google and grant Gmail access.")
        if st.button("Authenticate with Google"):
            auth_url = oauth.get_authorization_url()
            st.markdown(
                f"<meta http-equiv='refresh' content='0; url={auth_url}'/>",
                unsafe_allow_html=True
            )
            st.markdown(f"Or click [here]({auth_url}) if you’re not auto-redirected.")
        return

    # 3) If redirected back with a code, exchange it and save token
    if token is None and code:
        token = oauth.fetch_token(code)
        oauth.save_token(token)
        st.experimental_set_query_params()  # clear code from URL
        st.success("✅ Authentication successful!")

    # 4) We have a token—extract access_token
    access_token = token.get("access_token")
    if not access_token:
        st.warning("Access token missing from OAuth response.")
        return

    # 5) Input for Gmail search
    st.subheader("Gmail Search & Summarisation")
    query       = st.text_input("Search query", "subject:Demo")
    max_results = st.number_input("Max results", min_value=1, max_value=20, value=5)

    if st.button("📬 Summarise Emails"):
        with st.spinner("Fetching & summarising…"):
            summary = asyncio.run(
                EmailSummarizerPipeline(access_token).summarize(query, max_results)
            )
        st.markdown("**Email Subjects:**")
        st.text(summary)

    # 6) Logout button
    if st.button("Logout"):
        st.session_state.pop("token_data", None)



if __name__ == "__main__":
    main()

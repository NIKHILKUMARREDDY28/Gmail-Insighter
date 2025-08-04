import json
import asyncio
import streamlit as st
from config import *
from agent import get_emails_using_mcp
from cache import save_encrypted_cache
from uuid import uuid4

# ──────── App Configuration ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Google OAuth Email Summariser",
    page_icon="✉️",
    layout="wide"
)

# ──────── OAuth & Session Helpers ───────────────────────────────────────────────
def authenticate(oauth, code):
    token = oauth.fetch_token(code)
    oauth.save_token(token)
    st.session_state["session_id"] = str(uuid4())  # Generate a unique session ID
    save_encrypted_cache(st.session_state["session_id"], token, expire_in=3600)  # Save token in cache
    st.experimental_set_query_params()  # clear code from URL
    st.sidebar.success("✅ Authentication successful!")
    return token

# ──────── Caching for Summarisation ────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_and_summarize(access_token: str, query: str) -> list[str]:
    response = asyncio.run(get_emails_using_mcp(access_token, query))
    summaries: list[str] = []
    for msg in response:
        if msg.source == "critic_agent" and msg.type == "ToolCallSummaryMessage":
            args = json.loads(msg.tool_calls[0].arguments)
            if resp := args.get("response"):
                summaries.append(resp)
    return summaries

# ──────── Main Application ─────────────────────────────────────────────────────
def main():
    # Sidebar: Authentication & Controls
    with st.sidebar:
        st.header("🔑 Authentication")
        oauth = GoogleOAuth()
        token = oauth.get_saved_token()
        code = st.experimental_get_query_params().get("code", [None])[0]

        if not CLIENT_ID or not CLIENT_SECRET:
            st.error("🔐 Missing GOOGLE_CLIENT_ID / SECRET.")
            return

        if token is None and not code:
            if st.button("Connect to Gmail"):
                auth_url = oauth.get_authorization_url()
                st.markdown(f"[Click here to authenticate]({auth_url})", unsafe_allow_html=True)
            return
        if token is None and code:
            token = authenticate(oauth, code)

        access_token = token.get("access_token") if token else None
        if not access_token:
            st.warning("Access token not found.")
            return

        if st.button("Logout 🔒"):
            st.session_state.clear()
            st.rerun()

        if st.button("🗑️ Clear Conversation"):
            st.session_state.history = []
            st.rerun()

    # Ensure chat history exists
    if "history" not in st.session_state:
        st.session_state.history = []  # list of (role, content)

    # Main layout: header + chat area
    st.header("✉️ Gmail Search & Summarisation")
    st.markdown("---")

    chat_area = st.container()
    with chat_area:
        for role, content in st.session_state.history:
            with st.chat_message(role):
                st.markdown(content)

    # Input area: default chat_input
    prompt = st.chat_input("Type your Gmail query here and press Enter…")
    if prompt:
        # append user message
        st.session_state.history.append(("user", prompt))
        with st.spinner("Fetching & summarising emails…"):
            try:
                summaries = fetch_and_summarize(st.session_state["session_id"], prompt)
                if summaries:
                    for summary in summaries:
                        st.session_state.history.append(("assistant", summary))
                else:
                    st.session_state.history.append(("assistant", "*No summaries found for this query.*"))
            except Exception as e:
                st.session_state.history.append(("assistant", f"Error: {e}"))
        st.rerun()

if __name__ == "__main__":
    main()

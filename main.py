
from config import *
from agent import get_emails_using_mcp



# ──────── Streamlit App ────────────────────────────────────────────────────
async def main():
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
    st.code(access_token, language="text")
    # 5) Input for Gmail search
    st.subheader("Gmail Search & Summarisation")
    query       = st.text_input("Search query", "")
    max_results = st.number_input("Max results", min_value=1, max_value=20, value=5)

    if st.button("📬 Summarise Emails"):
        with st.spinner("Fetching & summarising…"):
            summary = await get_emails_using_mcp(access_token, query)
        st.markdown("**Email Subjects:**")
        st.code(summary, language="text")

    # 6) Logout button
    if st.button("Logout"):
        st.session_state.pop("token_data", None)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


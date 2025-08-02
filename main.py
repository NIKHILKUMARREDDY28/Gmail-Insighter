
import streamlit as st
from streamlit_google_auth import Authenticate
from settings import settings

st.title('Streamlit Google Auth Example')


authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name=settings.COOKIE_NAME,
    cookie_key=settings.COOKIE_SECRET,
    redirect_uri='http://localhost:8501',  # your app redirect URI
)

# Check if already authenticated
authenticator.check_authentification()

# Login button
result = authenticator.login()
print(result)

if st.session_state.get('connected'):
    st.image(st.session_state['user_info'].get('picture'))
    st.write('Hello, ' + st.session_state['user_info'].get('name'))
    st.write('Your email is ' + st.session_state['user_info'].get('email'))
    st.json(st.user)
    st.json(st.session_state['user_info'])

    if st.button('Log out'):
        authenticator.logout()




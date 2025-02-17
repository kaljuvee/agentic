import streamlit as st
import tweepy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
CALLBACK_URL = "http://localhost:8501/callback"  # Streamlit default port

def init_twitter_auth():
    """Initialize Twitter OAuth handler"""
    auth = tweepy.OAuthHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        callback=CALLBACK_URL
    )
    return auth

def main():
    st.title("Twitter OAuth Setup")
    
    # Initialize session state
    if 'oauth_token' not in st.session_state:
        st.session_state.oauth_token = None
    if 'oauth_verifier' not in st.session_state:
        st.session_state.oauth_verifier = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'access_token_secret' not in st.session_state:
        st.session_state.access_token_secret = None

    # Check if we're in the callback
    query_params = st.experimental_get_query_params()
    
    if 'oauth_token' in query_params and 'oauth_verifier' in query_params:
        # We're in the callback
        st.session_state.oauth_token = query_params['oauth_token'][0]
        st.session_state.oauth_verifier = query_params['oauth_verifier'][0]
        
        try:
            # Initialize auth with stored request token
            auth = init_twitter_auth()
            auth.request_token = {
                'oauth_token': st.session_state.oauth_token,
                'oauth_token_secret': st.session_state.oauth_verifier
            }
            
            # Get access token
            auth.get_access_token(st.session_state.oauth_verifier)
            
            # Store access tokens
            st.session_state.access_token = auth.access_token
            st.session_state.access_token_secret = auth.access_token_secret
            
            # Display success message and tokens
            st.success("Successfully authenticated with Twitter!")
            st.write("Add these tokens to your .env file:")
            st.code(f"""
TWITTER_ACCESS_TOKEN={auth.access_token}
TWITTER_ACCESS_TOKEN_SECRET={auth.access_token_secret}
            """)
            
        except Exception as e:
            st.error(f"Error during authentication: {str(e)}")
    
    elif not st.session_state.access_token:
        # Initial state - show login button
        st.write("Click below to authenticate with Twitter")
        
        if st.button("Connect to Twitter"):
            try:
                # Initialize new OAuth handler
                auth = init_twitter_auth()
                
                # Get authorization URL
                redirect_url = auth.get_authorization_url()
                
                # Redirect user to Twitter
                st.markdown(f'[Click here to authorize with Twitter]({redirect_url})')
                
            except Exception as e:
                st.error(f"Error initializing Twitter authentication: {str(e)}")
    
    else:
        # Already authenticated
        st.success("You're already authenticated with Twitter!")
        st.write("Your access tokens:")
        st.code(f"""
TWITTER_ACCESS_TOKEN={st.session_state.access_token}
TWITTER_ACCESS_TOKEN_SECRET={st.session_state.access_token_secret}
        """)

if __name__ == "__main__":
    main() 
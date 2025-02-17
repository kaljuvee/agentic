import streamlit as st
import tweepy
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Twitter API credentials - Using OAuth 2.0
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")  # Remove default value
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")  # Remove default value

# Update the callback URL handling
ALLOWED_CALLBACK_URLS = [
    "https://agentic-dcjz.onrender.com/callback",
    "http://localhost:8501/callback",
    "https://research.finespresso.org/callback"
]

def verify_env_variables():
    """Verify all required environment variables are set"""
    required_vars = ["TWITTER_CLIENT_ID", "TWITTER_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        st.stop()

def get_callback_url():
    """Get the appropriate callback URL based on the current host"""
    # Get the current URL from Streamlit
    current_url = st.experimental_get_query_params().get('callback_url', [''])[0]
    
    if not current_url:
        for url in ALLOWED_CALLBACK_URLS:
            if url in st.experimental_get_url():
                return url
        return ALLOWED_CALLBACK_URLS[0]
    
    if current_url in ALLOWED_CALLBACK_URLS:
        return current_url
    
    st.error(f"Invalid callback URL: {current_url}")
    st.stop()

def init_twitter_auth():
    """Initialize Twitter OAuth 2.0 handler"""
    callback_url = get_callback_url()
    
    # Using OAuth 2.0
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        redirect_uri=callback_url,
        scope=["tweet.read", "tweet.write", "users.read"]
    )
    return oauth2_user_handler

def callback_page():
    verify_env_variables()
    
    st.title("Twitter Authentication Callback")
    
    # Get query parameters
    query_params = st.experimental_get_query_params()
    
    if 'code' in query_params:  # OAuth 2.0 uses 'code' instead of oauth_token
        auth_code = query_params['code'][0]
        
        try:
            # Initialize auth handler
            auth = init_twitter_auth()
            
            # Get access token using the authorization code
            access_token = auth.fetch_token(auth_code)
            
            # Store tokens in session state
            st.session_state.access_token = access_token
            
            # Display success message
            st.success("🎉 Successfully authenticated with Twitter!")
            
            # Show the token
            st.write("### Your Twitter Access Token")
            st.info("Add this token to your .env file:")
            st.code(f"""
TWITTER_ACCESS_TOKEN={access_token}
            """)
            
            # Add testing options
            st.markdown("---")
            st.markdown("### Test Your Twitter Integration")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Test Connection"):
                    test_twitter_connection()
            
            with col2:
                if st.button("Post Test Tweet"):
                    test_tweet()
            
        except Exception as e:
            st.error(f"❌ Error during authentication: {str(e)}")
            st.markdown("Please try again from the [main page](/)")
    
    else:
        st.warning("⚠️ No authorization code found in the URL")
        st.markdown("Please start the authentication process from the [main page](/)")
        
        st.expander("Debug Information").write({
            "Query Parameters": query_params,
            "Session State": {k: v for k, v in st.session_state.items() if 'token' in k.lower()}
        })

def test_twitter_connection():
    """Test Twitter API connection and credentials"""
    try:
        client = tweepy.Client(bearer_token=st.session_state.get('access_token'))
        
        me = client.get_me()
        if me.data:
            st.success(f"✅ Successfully connected as @{me.data.username}")
            return True
        return False
        
    except Exception as e:
        st.error(f"❌ Connection test failed: {str(e)}")
        return False

def test_tweet():
    """Post a test tweet"""
    try:
        client = tweepy.Client(bearer_token=st.session_state.get('access_token'))
        
        response = client.create_tweet(
            text=f"Testing Twitter API integration with OAuth 2.0! 🤖 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if response.data:
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            st.success("✅ Test tweet posted successfully!")
            st.markdown(f"[View Tweet]({tweet_url})")
            return True
        return False
        
    except Exception as e:
        st.error(f"❌ Tweet test failed: {str(e)}")
        return False

if __name__ == "__main__":
    callback_page()

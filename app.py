from flask import Flask, request, jsonify, render_template, redirect, session
import importlib
import os
import json
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Twitter API credentials
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
CALLBACK_URL = "https://agentic-dcjz.onrender.com/callback"

def init_twitter_auth():
    """Initialize Twitter OAuth 2.0 handler"""
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        redirect_uri=CALLBACK_URL,
        scope=["tweet.read", "tweet.write", "users.read"]
    )
    return oauth2_user_handler

@app.route('/')
def index():
    """
    Serve the welcome page with the chat test interface
    """
    return render_template('index.html')

@app.route('/twitter-auth')
def twitter_auth():
    """
    Handle Twitter authentication initiation
    """
    try:
        # Initialize OAuth handler
        auth = init_twitter_auth()
        
        # Get authorization URL
        redirect_url = auth.get_authorization_url()
        
        # Store state in session
        session['oauth_state'] = auth.state
        
        # Redirect to Twitter
        return redirect(redirect_url)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/callback')
def callback():
    """
    Handle Twitter OAuth callback
    """
    try:
        # Get the authorization code
        code = request.args.get('code')
        state = request.args.get('state')
        
        # Verify state
        if state != session.get('oauth_state'):
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Initialize auth handler
        auth = init_twitter_auth()
        
        # Get access token
        access_token = auth.fetch_token(code)
        
        # Store token in session
        session['access_token'] = access_token
        
        # Redirect to success page
        return render_template('callback.html', 
                             success=True, 
                             access_token=access_token)
        
    except Exception as e:
        return render_template('callback.html', 
                             success=False, 
                             error=str(e))

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that routes requests to different agents
    """
    # Get parameters from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    query = data.get('query')
    agent = data.get('agent')
    
    if not query or not agent:
        return jsonify({"error": "Missing required parameters: 'query' and 'agent'"}), 400
    
    try:
        # Dynamically import the agent module
        module_path = f"examples.{agent}.langgraph.{agent}_agent"
        agent_module = importlib.import_module(module_path)
        
        # Get the response from the agent
        response = agent_module.get_response(query)
        
        # Extract the last message content
        if response and "messages" in response:
            last_message = response["messages"][-1].content
            return jsonify({"response": last_message})
        else:
            return jsonify({"error": "Invalid response from agent"}), 500
            
    except ImportError:
        return jsonify({"error": f"Agent '{agent}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Change the /swagger route to serve the UI instead of raw JSON
@app.route('/swagger')
def swagger():
    """
    Serve the Swagger UI interface
    """
    return render_template('swagger_ui.html')

# Add new route for the raw JSON
@app.route('/swagger.json')
def swagger_json():
    """
    Serve the Swagger JSON file
    """
    with open('static/swagger.json') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template
import importlib
import os

app = Flask(__name__)

@app.route('/')
def index():
    """
    Serve the welcome page with the chat test interface
    """
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)

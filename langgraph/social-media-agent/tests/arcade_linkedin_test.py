import os
from arcadepy import Arcade
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ARCADE_API_KEY")
USER_ID = os.getenv("LINKEDIN_USER_ID")

if not API_KEY:
    print("No Arcade API key found. Please set ARCADE_API_KEY in your .env file.")
    exit(1)

if not USER_ID:
    print("No LinkedIn user ID found. Please set LINKEDIN_USER_ID in your .env file.")
    exit(1)

client = Arcade(api_key=API_KEY)

# Authorize the tool
auth_response = client.tools.authorize(
    tool_name="Linkedin.CreateTextPost@0.1.10",
    user_id=USER_ID,
)

# Check if authorization is completed
if auth_response.status != "completed":
    print(f"Click this link to authorize: {auth_response.url}")

# Wait for the authorization to complete
auth_response = client.auth.wait_for_completion(auth_response)

if auth_response.status != "completed":
    raise Exception("Authorization failed")

print("🚀 Authorization successful!")

result = client.tools.execute(
    tool_name="Linkedin.CreateTextPost@0.1.10",
    input={
        "text": "Hello world"
    },
    user_id=USER_ID,
)

print(result)
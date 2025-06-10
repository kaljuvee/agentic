import os
from arcadepy import Arcade
from dotenv import load_dotenv

load_dotenv()

ARCADE_API_KEY = os.getenv("ARCADE_API_KEY")
TWITTER_USER_ID = os.getenv("TWITTER_USER_ID")
LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID")

print("ARCADE_API_KEY set:", bool(ARCADE_API_KEY))
print("TWITTER_USER_ID set:", bool(TWITTER_USER_ID))
print("LINKEDIN_USER_ID set:", bool(LINKEDIN_USER_ID))

if not ARCADE_API_KEY:
    print("No Arcade API key found. Please set ARCADE_API_KEY in your .env file.")
    exit(1)

client = Arcade(api_key=ARCADE_API_KEY)

# Try listing available tools
try:
    print("\nListing available tools:")
    tools = client.tools.list()
    for tool in tools:
        print(f"- {tool['name']}")
except Exception as e:
    print("Error listing tools:", e)

# Try a simple tool call (Math.Sqrt)
try:
    print("\nTesting Math.Sqrt tool:")
    response = client.tools.execute(
        tool_name="Math.Sqrt",
        input={"a": "16"},
        user_id="test@example.com"
    )
    print("Math.Sqrt(16) =", response.output.value)
except Exception as e:
    print("Error calling Math.Sqrt tool:", e)

# Try to check if Twitter.CreateTweet tool is available
try:
    print("\nTesting Twitter.CreateTweet tool (dry run):")
    if TWITTER_USER_ID:
        response = client.tools.execute(
            tool_name="Twitter.CreateTweet",
            input={"text": "Testing Arcade API key."},
            user_id=TWITTER_USER_ID
        )
        print("Twitter.CreateTweet response:", response.output.value)
    else:
        print("TWITTER_USER_ID not set, skipping Twitter test.")
except Exception as e:
    print("Error calling Twitter.CreateTweet tool:", e)

# Try to check if LinkedIn.CreatePost tool is available
try:
    print("\nTesting LinkedIn.CreatePost tool (dry run):")
    if LINKEDIN_USER_ID:
        response = client.tools.execute(
            tool_name="LinkedIn.CreatePost",
            input={"text": "Testing Arcade API key.", "user_id": LINKEDIN_USER_ID},
            user_id=LINKEDIN_USER_ID
        )
        print("LinkedIn.CreatePost response:", response.output.value)
    else:
        print("LINKEDIN_USER_ID not set, skipping LinkedIn test.")
except Exception as e:
    print("Error calling LinkedIn.CreatePost tool:", e) 
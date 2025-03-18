# NewsX - X-Posting Agent

A news commentary agent that fetches the latest headlines and posts neutral, professional summaries to Twitter/X.

Uses LangGraph and demonstrates concepts like:
- Structured LLM output
- Custom graph state management
- Custom graph output streaming
- Prompt construction
- Tool use
- FastAPI integration for real-time streaming responses

## Capabilities

- **News Fetching**: Retrieves the latest headlines from NewsAPI based on user queries
- **Neutral Commentary**: Generates professional, neutral commentary in the style of Reuters or Bloomberg
- **Twitter Integration**: Automatically posts commentary to Twitter/X
- **Streaming Responses**: Get real-time streaming responses from the agent
- **Conversation Memory**: Maintain conversation context with thread IDs

## Example Usage

**User**
_"news on president"_
_"news on stock market"_

**NewsX Agent**
_Fetches headlines, generates neutral commentary, and posts to Twitter in real-time_

## Running Locally

Create a `.env` file to store your environment variables. Do not commit this file to the repository.

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o
NEWS_API_KEY=your_newsapi_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_KEY_SECRET=your_twitter_api_key_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

### With Docker

```bash
docker build -t x-posting-agent .
docker run -p 8000:8000 x-posting-agent
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn run:app --reload
```

### Testing the Agent

You can test the agent using the provided test script which automatically runs a series of predefined news queries:

```bash
python tests/x_posting_agent_test.py
```

The test script will run the following queries:
- "news on president" - Presidential news in neutral style
- "news on stock market" - Stock market news in neutral style

## API Endpoints

- `/chat`: News posting agent endpoint

The endpoint accepts POST requests with the following JSON structure:
```json
{
  "input": "news on [topic]",
  "userId": "unique_user_id",
  "messageHistory": []
}
```

## Project Structure

- `graph/x_posting_agent.py`: Contains the news tools, model definitions, and LangGraph implementation
- `run.py`: FastAPI server that exposes the agent as an endpoint
- `tests/x_posting_agent_test.py`: Test script for the news agent

## Features

### Streaming Support

The agent supports streaming responses, allowing for real-time feedback as the agent processes news and generates commentary. This is implemented through:

- Asynchronous streaming with OpenAI's streaming capabilities
- Compatible with FastAPI's `StreamingResponse`
- Thread-based conversation tracking

### Neutral News Commentary

The agent is designed to provide neutral, professional commentary on news headlines:

- Factual reporting without bias
- Professional tone similar to Reuters or Bloomberg
- Concise format optimized for Twitter (under 270 characters)
- Automatic hashtag inclusion (#NewsX)

## Future Enhancements

- Support for more news categories and sources
- Image generation for news posts
- Scheduled posting of trending news
- User preference settings for news topics
- Multi-platform posting (Facebook, LinkedIn, etc.)
- Analytics on post engagement

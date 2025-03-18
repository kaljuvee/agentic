# Alpaca Agent API Usage Examples

## Basic Chat Request

```bash
curl -X POST http://localhost:8000/chat \
 -H "Content-Type: application/json" \
 -d '{
  "input": "Show me my account information",
  "history": [],
  "config": {
    "thread_id": "trading_session_123"
  }
}'
```

## Chat Request with History

```bash
curl -X POST http://localhost:8000/chat \
 -H "Content-Type: application/json" \
 -d '{
  "input": "What are my current positions?",
  "history": [
    {
      "role": "user",
      "content": "Show me my account information"
    },
    {
      "role": "agent",
      "content": "Your account has $10,000 in buying power and $15,000 in portfolio value."
    }
  ],
  "config": {
    "thread_id": "trading_session_123"
  }
}'
```

## Non-Streaming Request

```bash
curl -X POST http://localhost:8000/chat \
 -H "Content-Type: application/json" \
 -d '{
  "input": "Show me my account information",
  "history": [],
  "config": {
    "thread_id": "trading_session_123",
    "streaming": false
  }
}'
```

## Configuration Options

The `config` object supports the following options:

- `thread_id`: String identifier for the conversation thread (default: "trading_demo")
- `streaming`: Boolean to toggle between streaming and non-streaming responses (default: true)

## Response Format

### Streaming Response
Content-Type: text/event-stream

```
data: I'll check your account information.

data: Your account has a balance of $10,000.

data: Your buying power is currently $10,000.
```

### Non-Streaming Response
Content-Type: application/json

```json
{
  "response": "Your account has a balance of $10,000. Your buying power is currently $10,000."
}
``` 
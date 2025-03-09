# Comedy Roast Question Generator

A fun application that generates hilarious roasting questions about a person using AI and web search.

## Features

- Search for information about a person using DuckDuckGo
- Generate 5 funny roasting questions based on the search results
- Shows the AI's thought process and analysis of search results
- Simple and intuitive Streamlit interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your OpenAI API key and model:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL_NAME=gpt-4o-mini
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run Home.py
   ```
2. Enter a name in the text input field
3. Click "Generate Roast Questions"
4. Enjoy the hilarious roasting questions!

## Testing

You can test the roast agent without the Streamlit interface:

```
python run_tests.py
```

This will run tests with two sample names (Elon Musk and Taylor Swift) and display the results.

## How It Works

The application uses:
- LangGraph for orchestrating the AI workflow
- OpenAI's GPT-4o-mini model via LangChain (configurable via .env)
- DuckDuckGo Search API for gathering information
- Streamlit for the user interface

The roast generation process:
1. The app searches for information about the person using DuckDuckGo
2. The AI analyzes the search results and identifies interesting facts
3. Based on this information, it creates 5 hilarious roasting questions
4. The output includes both the AI's analysis and the roasting questions

## Project Structure

- `graph/roast_agent.py`: Contains the core logic for the roasting agent
- `Home.py`: Streamlit interface for the application
- `tests/roast_agent_test.py`: Test script for the roasting agent
- `run_tests.py`: Simple script to run the tests

## Troubleshooting

If you encounter any issues:

1. Make sure your OpenAI API key is correctly set in the `.env` file
2. Ensure you have the latest versions of the dependencies:
   ```
   pip install -U langchain-openai langchain-community pydantic
   ```
3. Check that you have a working internet connection for the DuckDuckGo search
4. If you get timeout errors, try again as it might be due to rate limiting
5. Try changing the model in your `.env` file if you're having issues with a specific model

## Tips for Better Results

- Try celebrities, politicians, athletes, or other public figures
- The more well-known the person, the better the roasts will be
- You can use the questions for comedy nights, roast battles, or just for fun!

## License

MIT

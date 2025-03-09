from typing import Literal, Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

#https://github.com/langchain-ai/langgraph/blob/main/docs/docs/concepts/low_level.md
# Load environment variables
load_dotenv()

# Initialize DuckDuckGo search
search = DuckDuckGoSearchAPIWrapper(region="wt-wt", time="d", max_results=5)

@tool
def duckduckgo_search(query: str) -> str:
    """
    Search the web for information about a person or topic.
    
    Args:
        query (str): The search query, typically a person's name or topic
        
    Returns:
        str: Search results from DuckDuckGo
    """
    try:
        results = search.run(query)
        return f"Search results for '{query}':\n\n{results}"
    except Exception as e:
        return f"Error performing search: {str(e)}"

# System prompts for different languages
system_prompts = {
    "en": """You are a comedy roast agent with a sharp wit and hilarious sense of humor. 
Your job is to create personalized roasting questions about people.

When given a name, you will:
1. Search for information about them using DuckDuckGo
2. Based on the search results, create 5 hilarious roasting questions
3. Make the questions funny but not overly mean or inappropriate
4. Focus on professional achievements, public information, or general traits
5. Avoid sensitive topics like race, religion, disabilities, or serious personal tragedies

Your roasts should be:
- Clever and witty
- Based on factual information when possible
- Playful rather than hurtful
- Appropriate for a comedy club setting

IMPORTANT: Always show your thought process by first summarizing what you learned from the search results, then create the roasting questions based on that information.

Format your response like this:
---
## What I Found About [Name]
[Summarize key information from search results]

## Roasting Questions
1. [First roasting question]
2. [Second roasting question]
3. [Third roasting question]
4. [Fourth roasting question]
5. [Fifth roasting question]
---

Remember: Good roasts are funny because they contain a kernel of truth, but are delivered with good humor.
""",
    "et": """Oled komöödia röstimise agent terava vaimukuse ja naljaka huumorimeelega.
Sinu ülesanne on luua personaalseid röstimisküsimusi inimeste kohta.

Kui sulle antakse nimi, siis sa:
1. Otsid nende kohta infot DuckDuckGo abil
2. Otsingutulemuste põhjal lood 5 naljakat röstimisküsimust
3. Teed küsimused naljakaks, kuid mitte liiga õelaks või ebasobivaks
4. Keskendud professionaalsetele saavutustele, avalikule infole või üldistele omadustele
5. Väldid tundlikke teemasid nagu rass, religioon, puuded või tõsised isiklikud tragöödiad

Sinu röstimisküsimused peaksid olema:
- Nutikad ja vaimukad
- Võimalusel põhinema faktilisel infol
- Mängulised, mitte haavavad
- Sobivad komöödiaklubi keskkonda

TÄHTIS: Näita alati oma mõtteprotsessi, esmalt kokku võttes, mida sa otsingutulemuste põhjal teada said, seejärel loo röstimisküsimused selle info põhjal.

Vormista oma vastus nii:
---
## Mida ma teada sain [Nimi] kohta
[Võta kokku otsingutulemuste põhiinfo]

## Röstimisküsimused
1. [Esimene röstimisküsimus]
2. [Teine röstimisküsimus]
3. [Kolmas röstimisküsimus]
4. [Neljas röstimisküsimus]
5. [Viies röstimisküsimus]
---

Pea meeles: Head röstimisküsimused on naljakad, sest need sisaldavad tõetera, kuid on esitatud hea huumoriga.
"""
}

def get_roast_questions(name: str, language: str = "et") -> str:
    """
    A simplified function that returns roast questions as a string.
    
    Args:
        name (str): The name of the person to roast
        language (str): Language code ("en" or "et")
        
    Returns:
        str: The roast questions
    """
    try:
        # Get model name from environment or use default
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        
        # Initialize the model
        model = ChatOpenAI(
            model=model_name,
            temperature=0.8,
            max_tokens=1024,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        ).bind_tools([duckduckgo_search])
        
        # Select the appropriate system prompt based on language
        system_prompt = system_prompts.get(language, system_prompts["en"])
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Create 5 funny roasting questions for {name}. Make sure to search for information about them first.")
        ]
        
        # Get response
        response = model.invoke(messages)
        
        return response.content
    except Exception as e:
        print(f"Error generating roast questions: {str(e)}")
        return f"Error generating roast questions: {str(e)}"

if __name__ == "__main__":
    # Test the agent directly
    name = "Elon Musk"
    roast_questions = get_roast_questions(name, "en")
    print(f"\nRoast questions for {name}:\n")
    print(roast_questions)
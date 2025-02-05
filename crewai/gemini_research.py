import os
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process
from langchain.tools import DuckDuckGoSearchRun

def create_agents(llm):
    """Create and return researcher and writer agents"""
    
    # Create search tool
    search_tool = DuckDuckGoSearchRun()
    
    # Create researcher agent
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover cutting-edge developments in AI and data science',
        backstory="""You work at a leading tech think tank.
        Your expertise lies in identifying emerging trends.
        You have a knack for dissecting complex data and presenting
        actionable insights.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )
    
    # Create writer agent
    writer = Agent(
        role='Tech Content Strategist',
        goal='Craft compelling content on tech advancements',
        backstory="""You are a renowned Content Strategist, known for
        your insightful and engaging articles.
        You transform complex concepts into compelling narratives.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[]
    )
    
    return researcher, writer

def create_tasks(researcher, writer):
    """Create and return research and writing tasks"""
    
    # Research task
    task1 = Task(
        description="""Conduct a comprehensive analysis of the latest advancements in AI in 2024.
        Identify key trends, breakthrough technologies, and potential industry impacts.
        Your final answer MUST be a full analysis report""",
        agent=researcher
    )
    
    # Writing task
    task2 = Task(
        description="""Using the insights provided, develop an engaging blog
        post that highlights the most significant AI advancements.
        Your post should be informative yet accessible, catering to a tech-savvy audience.
        Make it sound cool, avoid complex words so it doesn't sound like AI.
        Your final answer MUST be the full blog post of at least 4 paragraphs.""",
        agent=writer
    )
    
    return [task1, task2]

def main():
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        verbose=True,
        temperature=0.6,
        google_api_key=os.getenv("GOOGLE_API_KEY")  # Make sure to set this environment variable
    )
    
    # Create agents
    researcher, writer = create_agents(llm)
    
    # Create tasks
    tasks = create_tasks(researcher, writer)
    
    # Create crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=tasks,
        verbose=2
    )
    
    # Start the crew's work
    result = crew.kickoff()
    
    # Print the result
    print("\nFinal Blog Post:")
    print("-" * 50)
    print(result)

if __name__ == "__main__":
    main()

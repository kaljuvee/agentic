from setuptools import setup, find_packages

setup(
    name="social-media-agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "arcadepy",
        "langchain-openai",
        "langgraph",
        "python-dotenv",
    ],
) 
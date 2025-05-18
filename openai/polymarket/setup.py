from setuptools import setup, find_packages

setup(
    name="polymarket-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "openai",
        "openai-agents",
        "pandas",
        "requests",
        "python-dotenv",
    ],
) 
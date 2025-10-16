#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#     "pydantic-ai==1.1.0",
#     "python-dotenv==1.0.1",
# ]
# ///

from dotenv import load_dotenv

from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

# Create a simple agent with Claude Sonnet 4.0
agent = Agent("anthropic:claude-sonnet-4-0", instructions="Be concise, reply with one sentence.")

# Run the agent synchronously with a simple prompt
result = agent.run_sync('Where does "hello world" come from?')
print(result.output)

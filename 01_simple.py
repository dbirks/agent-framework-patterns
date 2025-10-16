#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#     "pydantic-ai==1.1.0",
#     "python-dotenv==1.0.1",
# ]
# ///

import os

from dotenv import load_dotenv

from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

# Get model from environment or use default
model = os.getenv("MODEL", "anthropic:claude-sonnet-4-0")

# Create a simple agent with the configured model
agent = Agent(model, instructions="Be concise, reply with one sentence.")

# Run the agent synchronously with a simple prompt
result = agent.run_sync('Where does "hello world" come from?')
print(result.output)

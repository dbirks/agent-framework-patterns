#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Create a simple agent with the configured model
agent = Agent(model, instructions="Be concise, reply with one sentence.")

# Run the agent synchronously with a simple prompt
result = agent.run_sync("What character says 'hello there'?")
print(result.output)

#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os
import sys

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Create an agent
agent = Agent(
    model,
    system_prompt="You're a creative storyteller. Write engaging, descriptive stories.",
)

# Run the agent with streaming enabled
print("📖 Streaming Response Demo")
print("=" * 50)
print("\nStreaming story...\n")

# Stream the response token by token
for chunk in agent.run_stream("Write a short story about a robot learning to paint."):
    print(chunk, end="", flush=True)
    sys.stdout.flush()

print("\n\n✅ Stream complete!")

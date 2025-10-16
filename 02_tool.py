#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os
import random

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv(override=True)
model = os.getenv("MODEL")

# Create an agent with a system prompt
agent = Agent(
    model,
    system_prompt="You're a helpful assistant that can roll dice for the user.",
)


# Define a tool using the @agent.tool_plain decorator
@agent.tool_plain
def roll_die(sides: int = 6) -> str:
    """Roll a die with the specified number of sides (default is 6) and return the result."""
    result = random.randint(1, sides)
    return f"Rolled a {sides}-sided die: {result}"


# Run the agent with a user prompt
result = agent.run_sync("Roll a 20-sided die for me")
print(result.output)

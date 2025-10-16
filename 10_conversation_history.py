#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "rich==14.2.0",
# ]
# ///
"""
Conversation History

Demonstrates multi-turn conversations by passing message_history between agent runs.
Shows how agents maintain context across multiple interactions. The agent asks
questions to gather travel preferences and remembers details throughout.
"""

import os
from textwrap import dedent

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from rich.prompt import Prompt

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

agent = Agent(
    model,
    system_prompt=dedent(
        """
        You're a travel planning assistant. Ask the user questions to learn about
        their travel preferences, then provide personalized recommendations.
        Remember all details from the conversation.
        """
    ).strip(),
)

print("Travel Planning Assistant\n")

# Start the conversation - let the agent initiate
result = agent.run_sync("Start helping me plan a trip.")
print(f"Assistant: {result.output}\n")

message_history = result.new_messages()

# Interactive conversation loop
while True:
    user_input = Prompt.ask("You")

    if user_input.lower() in ["exit", "quit", "done"]:
        break

    result = agent.run_sync(user_input, message_history=message_history)
    print(f"Assistant: {result.output}\n")

    message_history = result.new_messages()

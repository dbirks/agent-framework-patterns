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
Shows how agents maintain context across multiple interactions in a simple chat loop.
"""

import os

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
    system_prompt="You're a helpful assistant. Remember details from the conversation.",
)

print("Chat with the assistant. Type 'exit' to quit.\n")

message_history = None

while True:
    user_input = Prompt.ask("[bold blue]You[/bold blue]")

    if user_input.lower() in ["exit", "quit"]:
        break

    result = agent.run_sync(user_input, message_history=message_history)
    print(f"[bold green]Assistant[/bold green]: {result.output}\n")

    message_history = result.new_messages()

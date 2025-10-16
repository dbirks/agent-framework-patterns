#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///
"""
Human-in-the-Loop Example

Demonstrates interactive approval workflow where the agent requests user confirmation
before performing sensitive operations. Tools can prompt for user input to ensure
human oversight of critical actions like file deletion or modification.
"""

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Create an agent
agent = Agent(model, system_prompt="You're a helpful file organizer assistant.")


# Tool that requires human approval
@agent.tool_plain
def delete_file(filename: str) -> str:
    """Delete a file (requires user confirmation)."""
    print(f"\n🤔 Agent wants to delete: {filename}")
    response = input("Approve? (y/n): ").strip().lower()
    if response == "y":
        return f"File '{filename}' deleted successfully"
    else:
        return "Operation cancelled by user"


@agent.tool_plain
def move_file(filename: str, destination: str) -> str:
    """Move a file to a new location (requires user confirmation)."""
    print(f"\n🤔 Agent wants to move: {filename} -> {destination}")
    response = input("Approve? (y/n): ").strip().lower()
    if response == "y":
        return f"Moved '{filename}' to '{destination}'"
    else:
        return "Operation cancelled by user"


# Run the agent
print("🤖 File Organizer Agent (Human-in-the-Loop)")
print("=" * 50)
result = agent.run_sync("I have old_report.txt and backup.log taking up space. Can you help clean them up?")
print(f"\n✅ Final response: {result.output}")

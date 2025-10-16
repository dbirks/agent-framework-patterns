#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///
"""
Conversation History

Demonstrates multi-turn conversations by passing message_history between agent runs.
The agent maintains context across multiple interactions, remembering previous exchanges
to provide coherent, contextual responses. Essential for chatbot and assistant applications.
"""

import os

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

# Create a travel planning assistant
agent = Agent(
    model,
    system_prompt="You're a helpful travel planning assistant. Remember details from the conversation to provide personalized recommendations.",
)

print("✈️  Travel Planning Assistant (Conversation History Demo)")
print("=" * 60)
print("This demo shows how agents maintain context across multiple turns.\n")

# Turn 1: User states their destination
print("👤 User: I'm planning a trip to Tokyo in spring")
result1 = agent.run_sync("I'm planning a trip to Tokyo in spring")
print(f"🤖 Assistant: {result1.output}\n")

# Turn 2: Follow-up question (agent should remember Tokyo & spring)
print("👤 User: What should I pack?")
result2 = agent.run_sync(
    "What should I pack?",
    message_history=result1.new_messages(),  # Pass conversation history
)
print(f"🤖 Assistant: {result2.output}\n")

# Turn 3: Another follow-up (agent should remember destination & packing context)
print("👤 User: Any food recommendations?")
result3 = agent.run_sync(
    "Any food recommendations?",
    message_history=result2.new_messages(),  # Continue the conversation
)
print(f"🤖 Assistant: {result3.output}\n")

# Turn 4: Test if agent remembers all context
print("👤 User: Should I visit in the beginning or end of the season?")
result4 = agent.run_sync(
    "Should I visit in the beginning or end of the season?",
    message_history=result3.new_messages(),
)
print(f"🤖 Assistant: {result4.output}\n")

print("=" * 60)
print("✅ Notice how the agent maintains context throughout the conversation!")
print("   - It remembers Tokyo as the destination")
print("   - It recalls spring as the season")
print("   - It builds on previous exchanges naturally")

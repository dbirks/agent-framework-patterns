#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "httpx==0.28.1",
# ]
# ///
"""
Multiple Tool Calls

Demonstrates an agent using multiple tools to answer a complex question.
Shows how the agent can call different tools to gather information and synthesize
a comprehensive answer. Features real weather API integration with Logfire observability.
"""

import os

import httpx
import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Configure Logfire for local development (no sending to the cloud)
logfire.configure(send_to_logfire=False)

# Instrument PydanticAI to track all agent operations
logfire.instrument_pydantic_ai()

# Create a weather agent with multiple tools
agent = Agent(
    model,
    system_prompt="You're a helpful weather assistant. Use the available tools to answer questions about weather.",
    instrument=True,
)


@agent.tool_plain
def get_weather(city: str) -> str:
    """Fetch current temperature for a specific city from wttr.in API."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        logfire.info(f"Fetching weather for {city}")

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        current = data["current_condition"][0]
        temp_f = current["temp_F"]

        result = f"{city} is currently {temp_f}°F"
        logfire.info(f"Weather retrieved: {city} = {temp_f}°F")
        return result

    except Exception as e:
        logfire.error(f"Weather fetch failed for {city}: {e}")
        return f"Unable to fetch weather for {city}"


result = agent.run_sync("What's the temperature in Tokyo, Sydney, and London right now?")

print()
print("=" * 70)
print(f"🤖 Agent Response:\n\n{result.output}")
print()

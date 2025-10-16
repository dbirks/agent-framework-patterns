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

# Configure Logfire for local development (no cloud sending)
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
        logfire.info("Fetching weather", city=city)

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        current = data["current_condition"][0]
        temp_f = current["temp_F"]

        result = f"{city} is currently {temp_f}°F"
        logfire.info("Weather retrieved", city=city, temp_f=temp_f)
        return result

    except Exception as e:
        logfire.error("Weather fetch failed", city=city, error=str(e))
        return f"Unable to fetch weather for {city}"


@agent.tool_plain
def convert_temperature(temp_f: float) -> str:
    """Convert Fahrenheit temperature to Celsius."""
    temp_c = round((temp_f - 32) * 5 / 9, 1)
    logfire.info("Temperature converted", temp_f=temp_f, temp_c=temp_c)
    return f"{temp_f}°F is {temp_c}°C"


@agent.tool_plain
def get_timezone(city: str) -> str:
    """Get the timezone for a city."""
    # Simple timezone data
    city_timezones = {
        "New York": "EST (UTC-5)",
        "London": "GMT (UTC+0)",
        "Tokyo": "JST (UTC+9)",
        "Sydney": "AEST (UTC+10)",
        "Paris": "CET (UTC+1)",
    }

    timezone = city_timezones.get(city, "Unknown timezone")
    result = f"{city} is in {timezone}"
    logfire.info("Timezone retrieved", city=city, timezone=timezone)
    return result


# Run the agent with a complex query that requires multiple tool calls
print("🔧 Multiple Tool Calls Demo")
print("=" * 70)
print()

query = """What's the temperature in Tokyo and Sydney right now?
Also convert 75°F to Celsius, and tell me what timezone London is in."""

print(f"👤 User: {query}")
print()
print("🤖 Agent is calling multiple tools to answer your question...")
print()

result = agent.run_sync(query)

print("=" * 70)
print(f"🤖 Agent Response:\n\n{result.output}")
print()
print("=" * 70)
print("✅ The agent called multiple tools to gather this information:")
print("   • get_weather() - fetched temperature for cities")
print("   • convert_temperature() - converted Fahrenheit to Celsius")
print("   • get_timezone() - looked up timezone information")
print("✅ Check Logfire output above to see each tool call traced")

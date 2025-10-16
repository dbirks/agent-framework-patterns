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
    """Fetch current weather for a specific city from wttr.in API."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        logfire.info("Fetching weather", city=city)

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        current = data["current_condition"][0]
        temp_f = current["temp_F"]
        condition = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind = current["windspeedMiles"]

        result = f"{city}: {temp_f}°F, {condition}, {humidity}% humidity, {wind} mph wind"
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
def compare_cities(city1: str, city2: str) -> str:
    """Compare basic facts about two cities."""
    # Simple comparison data
    city_info = {
        "New York": {"population": "8.3M", "timezone": "EST"},
        "London": {"population": "9.0M", "timezone": "GMT"},
        "Tokyo": {"population": "14M", "timezone": "JST"},
        "Sydney": {"population": "5.3M", "timezone": "AEST"},
    }

    info1 = city_info.get(city1, {"population": "Unknown", "timezone": "Unknown"})
    info2 = city_info.get(city2, {"population": "Unknown", "timezone": "Unknown"})

    result = f"{city1}: {info1['population']} population, {info1['timezone']} timezone. {city2}: {info2['population']} population, {info2['timezone']} timezone."
    logfire.info("Cities compared", city1=city1, city2=city2)
    return result


# Run the agent with a complex query that requires multiple tool calls
print("🔧 Multiple Tool Calls Demo")
print("=" * 70)
print()

query = """What's the weather in New York and London right now?
Also, if New York is at 72°F, what's that in Celsius?
And how do these two cities compare in terms of population?"""

print(f"👤 User: {query}")
print()
print("🤖 Agent is calling multiple tools to answer your question...")
print()

result = agent.run_sync(query)

print("=" * 70)
print(f"🤖 Agent Response:\n\n{result.output}")
print()
print("=" * 70)
print("✅ The agent called multiple tools:")
print("   • get_weather() - for New York and London")
print("   • convert_temperature() - for Fahrenheit to Celsius conversion")
print("   • compare_cities() - for population comparison")
print("✅ Check Logfire output above to see the tool call traces")

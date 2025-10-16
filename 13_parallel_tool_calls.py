#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///
"""
Parallel Tool Calls

Demonstrates concurrent tool execution where the agent calls multiple independent tools
to gather comprehensive information. The model can execute tool calls in parallel when
they don't depend on each other, improving performance for complex queries.
"""

import os
import random
import time

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Create an agent that aggregates city information
agent = Agent(
    model,
    system_prompt="You're a travel information assistant that provides comprehensive city overviews by gathering data from multiple sources.",
)


# Simulate API call delay for demonstration
def simulate_api_call(duration: float = 0.5):
    time.sleep(duration)


@agent.tool_plain
def get_weather(city: str) -> dict:
    """Get current weather information for a city."""
    print(f"   🌤️  Fetching weather for {city}...")
    simulate_api_call(0.3)

    weather_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Clear"]
    return {
        "city": city,
        "temperature": random.randint(15, 30),
        "condition": random.choice(weather_conditions),
        "humidity": random.randint(40, 80),
    }


@agent.tool_plain
def get_local_time(city: str) -> dict:
    """Get current local time and timezone for a city."""
    print(f"   🕐 Fetching local time for {city}...")
    simulate_api_call(0.3)

    # Simulate different timezones
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return {"city": city, "time": f"{hours:02d}:{minutes:02d}", "timezone": "Local Time"}


@agent.tool_plain
def get_popular_attractions(city: str) -> list:
    """Get top tourist attractions for a city."""
    print(f"   🗼 Fetching attractions for {city}...")
    simulate_api_call(0.4)

    attractions_db = {
        "Tokyo": ["Tokyo Tower", "Senso-ji Temple", "Shibuya Crossing", "Meiji Shrine"],
        "Paris": ["Eiffel Tower", "Louvre Museum", "Notre-Dame", "Arc de Triomphe"],
        "New York": ["Statue of Liberty", "Central Park", "Times Square", "Empire State Building"],
        "London": ["Big Ben", "Tower Bridge", "British Museum", "Buckingham Palace"],
    }
    return attractions_db.get(city, ["Historic District", "City Center", "Local Museum"])[:3]


@agent.tool_plain
def get_transport_options(city: str) -> dict:
    """Get available transportation options in a city."""
    print(f"   🚇 Fetching transport info for {city}...")
    simulate_api_call(0.3)

    return {
        "city": city,
        "metro": random.choice([True, False]),
        "bike_sharing": True,
        "taxi_apps": ["Uber", "Local Taxi"],
        "airport_distance_km": random.randint(15, 50),
    }


@agent.tool_plain
def get_average_costs(city: str) -> dict:
    """Get average daily costs for tourists in a city."""
    print(f"   💰 Fetching cost information for {city}...")
    simulate_api_call(0.3)

    return {
        "city": city,
        "meal_cost": random.randint(10, 30),
        "hotel_cost": random.randint(80, 200),
        "transport_day_pass": random.randint(5, 15),
        "currency": "USD",
    }


# Run the agent with a comprehensive question
print("🌍 Parallel Tool Calls Demo")
print("=" * 70)
print("Agent will call multiple independent tools to gather information\n")

city = "Tokyo"
question = f"Give me a comprehensive overview of {city} for a tourist: weather, local time, top attractions, transport, and daily costs."

print(f"👤 User: {question}\n")
print("🤖 Agent is gathering information from multiple sources:")

start_time = time.time()
result = agent.run_sync(question)
elapsed_time = time.time() - start_time

print(f"\n🤖 Agent Response:\n{result.output}\n")

print("=" * 70)
print(f"⚡ Total execution time: {elapsed_time:.2f} seconds")
print("\n✅ Notice how the agent:")
print("   - Called multiple tools to gather comprehensive information")
print("   - The model may call tools in parallel when possible")
print("   - Synthesized all data into a coherent response")

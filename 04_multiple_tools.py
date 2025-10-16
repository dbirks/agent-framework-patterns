#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "logfire==2.11.0",
# ]
# ///

import os
import random

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
    system_prompt="You're a helpful weather assistant that can check weather and convert temperatures.",
    instrument=True,
)


@agent.tool_plain
def get_current_weather(city: str) -> dict:
    """Get the current weather for a city."""
    # Simulate weather data
    conditions = ["sunny", "cloudy", "rainy", "snowy"]
    temp_f = random.randint(32, 95)
    weather_data = {
        "city": city,
        "temperature": temp_f,
        "unit": "fahrenheit",
        "condition": random.choice(conditions),
    }
    logfire.info("Weather data retrieved", city=city, temperature=temp_f)
    return weather_data


@agent.tool_plain
def get_forecast(city: str, days: int = 3) -> list:
    """Get weather forecast for the next few days."""
    forecast = []
    for i in range(days):
        forecast.append(
            {
                "day": i + 1,
                "high": random.randint(60, 90),
                "low": random.randint(40, 65),
                "condition": random.choice(["sunny", "cloudy", "rainy"]),
            }
        )
    logfire.info("Forecast generated", city=city, days=days)
    return forecast


@agent.tool_plain
def convert_temperature(temperature: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between fahrenheit and celsius."""
    if from_unit.lower() == "fahrenheit" and to_unit.lower() == "celsius":
        result = round((temperature - 32) * 5 / 9, 1)
    elif from_unit.lower() == "celsius" and to_unit.lower() == "fahrenheit":
        result = round(temperature * 9 / 5 + 32, 1)
    else:
        result = temperature
    logfire.info("Temperature converted", temperature=temperature, from_unit=from_unit, to_unit=to_unit, result=result)
    return result


# Run the agent with multiple tool calls
print("🔥 Multiple Tools with Logfire Demo")
print("=" * 50)
result = agent.run_sync(
    "What's the weather in San Francisco? Also give me the forecast and convert the current temp to celsius."
)
print(f"\nResult: {result.output}")
print("\n✅ Check Logfire output above for traced operations")

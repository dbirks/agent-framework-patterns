#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "httpx==0.28.1",
#   "rich==14.2.0",
# ]
# ///
"""
Structured Outputs with Rich Tables

Demonstrates structured output using Pydantic models combined with Rich table visualization.
The agent fetches real weather data for multiple cities worldwide using wttr.in API,
returns typed WeatherReport objects, and displays results in a beautiful formatted table.
Shows how to combine type-safe outputs with professional data presentation.
"""

import os
from textwrap import dedent

import httpx
import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from rich.console import Console
from rich.table import Table

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()


# Structured weather data models
class WeatherCondition(BaseModel):
    """Current weather conditions for a city"""

    city: str = Field(description="City name")
    temp_f: int = Field(description="Temperature in Fahrenheit")
    temp_c: int = Field(description="Temperature in Celsius")
    feels_like_f: int = Field(description="Feels like temperature in Fahrenheit")
    condition: str = Field(description="Weather condition description")
    humidity: int = Field(description="Humidity percentage")
    wind_speed_mph: int = Field(description="Wind speed in MPH")
    wind_dir: str = Field(description="Wind direction")


class WeatherReport(BaseModel):
    """Multiple city weather report"""

    cities: list[WeatherCondition] = Field(description="Weather data for multiple cities")


# Create a weather agent with structured output
agent = Agent(
    model,
    output_type=WeatherReport,
    system_prompt=dedent(
        """
        You're a global weather assistant that fetches real-time weather data for multiple cities.
        When asked about weather, use the get_weather tool to fetch data for major cities around the world.
        Return structured data for all cities in the WeatherReport format.
        """
    ).strip(),
    instrument=True,
)


@agent.tool_plain
def get_weather(city: str) -> dict:
    """Fetch real weather data from wttr.in API for a specific city."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        logfire.info("Fetching weather", city=city, url=url)

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        # Extract current conditions
        current = data["current_condition"][0]

        weather_data = {
            "city": city,
            "temp_f": int(current["temp_F"]),
            "temp_c": int(current["temp_C"]),
            "feels_like_f": int(current["FeelsLikeF"]),
            "condition": current["weatherDesc"][0]["value"],
            "humidity": int(current["humidity"]),
            "wind_speed_mph": int(current["windspeedMiles"]),
            "wind_dir": current["winddir16Point"],
        }

        logfire.info("Weather retrieved", city=city, temp_f=weather_data["temp_f"])
        return weather_data

    except Exception as e:
        logfire.error("Weather fetch failed", city=city, error=str(e))
        return {
            "city": city,
            "temp_f": 0,
            "temp_c": 0,
            "feels_like_f": 0,
            "condition": "Unable to fetch",
            "humidity": 0,
            "wind_speed_mph": 0,
            "wind_dir": "N/A",
        }


# Run the agent
print("🌍 Real-Time Global Weather Monitor")
print("=" * 70)
print()

result = agent.run_sync(
    dedent(
        """
        Get the current weather for these locations around the world:
        New York, London, Tokyo, Sydney, Paris, Dubai, São Paulo, Cairo (Egypt),
        Beijing (China), Moscow (Russia), Portland (Oregon), Mexico City, and
        McMurdo Station (Antarctica).
        Fetch weather for all of them.
        """
    ).strip()
)

weather_report: WeatherReport = result.output

# Create Rich table for display
console = Console()
table = Table(title="🌤️  Current Weather Around the World (Real-time Data)", show_header=True)

table.add_column("City", style="bold yellow", no_wrap=True)
table.add_column("Temp", justify="right", style="bold red")
table.add_column("Feels Like", justify="right", style="magenta")
table.add_column("Condition", style="green")
table.add_column("Humidity", justify="right", style="blue")
table.add_column("Wind", justify="right", style="cyan")

# Add rows for each city
for city_weather in weather_report.cities:
    table.add_row(
        city_weather.city,
        f"{city_weather.temp_f}°F",
        f"{city_weather.feels_like_f}°F",
        city_weather.condition,
        f"{city_weather.humidity}%",
        f"{city_weather.wind_speed_mph} mph {city_weather.wind_dir}",
    )

print()
console.print(table)
print()
print("=" * 70)
print("✅ Weather data sourced from wttr.in")
print("✅ Check Logfire output above for traced operations")
print(f"✅ Retrieved data for {len(weather_report.cities)} cities")

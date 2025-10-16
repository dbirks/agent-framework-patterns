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

# Create an agent with instrumentation enabled
agent = Agent(model, system_prompt="You're a math helper.", instrument=True)


@agent.tool_plain
def calculate(expression: str) -> float:
    """Safely evaluate a simple math expression."""
    try:
        # Only allow basic math operations for safety
        allowed_chars = set("0123456789+-*/.()")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return "Error: Invalid characters in expression"
        result = eval(expression)
        logfire.info("Calculation performed", expression=expression, result=result)
        return result
    except Exception as e:
        logfire.error("Calculation failed", expression=expression, error=str(e))
        return f"Error: {e}"


# Run the agent - all operations will be logged
print("🔥 Logfire Instrumentation Demo")
print("=" * 50)
result = agent.run_sync("What is 15 * 8 + 42?")
print(f"\nResult: {result.output}")
print("\n✅ Check Logfire output above for traced operations")

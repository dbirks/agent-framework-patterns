#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Create specialized sub-agents
research_agent = Agent(
    model,
    system_prompt="You're a research specialist. Provide factual, concise information about topics.",
)

writing_agent = Agent(
    model,
    system_prompt="You're a creative writer. Transform information into engaging, well-written content.",
)

# Create main coordinator agent
coordinator = Agent(
    model,
    system_prompt="You're a coordinator that delegates tasks to specialist agents.",
)


# Tool that calls the research agent
@coordinator.tool_plain
def research_topic(topic: str) -> str:
    """Research a topic using the specialized research agent."""
    print(f"📚 Research agent investigating: {topic}")
    result = research_agent.run_sync(f"Provide key facts about: {topic}")
    return result.output


# Tool that calls the writing agent
@coordinator.tool_plain
def write_content(information: str, style: str = "engaging") -> str:
    """Write content using the specialized writing agent."""
    print(f"✍️  Writing agent creating {style} content...")
    result = writing_agent.run_sync(f"Write {style} content based on this information: {information}")
    return result.output


# Run the coordinator - it will delegate to sub-agents
print("🎯 Agent Composition Demo")
print("=" * 50)
result = coordinator.run_sync(
    "I need an engaging article about quantum computing. First research it, then write compelling content."
)
print(f"\n✅ Final output:\n{result.output}")

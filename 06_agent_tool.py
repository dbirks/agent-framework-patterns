#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai[duckduckgo]==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.common_tools import duckduckgo_search_tool

# Load environment variables from .env file
load_dotenv(override=True)

# Create specialized sub-agents with specific models
research_agent = Agent(
    "anthropic:claude-haiku-4-5",
    system_prompt="You're a research specialist. Search the web for factual, up-to-date information about topics. Use the search tool to gather current information.",
    tools=[duckduckgo_search_tool],
)

writing_agent = Agent(
    "openai:o4-mini",
    system_prompt="You're a creative writer. Transform information into engaging, well-written content with clear structure and compelling narrative.",
)

# Create main coordinator agent
coordinator = Agent(
    "anthropic:claude-haiku-4-5",
    system_prompt="You're a coordinator that delegates tasks to specialist agents. Use research_topic to gather information, then write_content to create engaging content.",
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

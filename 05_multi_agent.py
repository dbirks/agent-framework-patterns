#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "ddgs==9.6.1",
#   "rich==14.2.0",
# ]
# ///
"""
Agent Composition with Web Search

Demonstrates agent composition where a coordinator delegates to specialized sub-agents.
The research agent (Claude Haiku 4.5) searches the web using DuckDuckGo for current information,
while the writing agent (OpenAI o4-mini) transforms that information into engaging content.
Shows how different models can be used for different specialized tasks.
"""

import os
from typing import cast

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()


class Article(BaseModel):
    content: str = Field(description="The full article content as flowing prose paragraphs")


# Create specialized sub-agents with specific models
research_agent = Agent(
    "anthropic:claude-haiku-4-5",
    system_prompt="You're a research specialist. Search the web for factual, up-to-date information about topics. Use the search tool to gather current information from at least 5 different articles or sources.",
    tools=[duckduckgo_search_tool()],
    instrument=True,
)

writing_agent = Agent(
    "openai:o4-mini",
    system_prompt="You're a creative writer. Transform information into engaging prose. Write in a natural, flowing narrative style with clear paragraphs. Focus on storytelling and making complex topics accessible.",
    instrument=True,
)

# Create main coordinator agent
coordinator = Agent(
    "anthropic:claude-haiku-4-5",
    output_type=Article,
    system_prompt="You're a coordinator that delegates tasks to specialist agents. Use research_topic to gather information, then write_content to create the article. Return the final article content in the Article format.",
    instrument=True,
)


# Tool that calls the research agent
@coordinator.tool_plain
def research_topic(topic: str) -> str:
    """Research a topic using the specialized research agent."""
    logfire.info(f"Research agent investigating: {topic}")
    result = research_agent.run_sync(f"Provide key facts about: {topic}")
    return result.output


# Tool that calls the writing agent
@coordinator.tool_plain
def write_content(information: str, style: str = "engaging") -> str:
    """Write content using the specialized writing agent."""
    logfire.info(f"Writing agent creating {style} content")
    result = writing_agent.run_sync(f"Write {style} prose based on this information: {information}")
    return result.output


console.print("\n[bold cyan]Multi-agent demo[/bold cyan]\n")

logfire.info("Starting multi-agent workflow")
result = coordinator.run_sync(
    "I need an engaging article about quantum computing. First research it, then write compelling prose content."
)

article = cast(Article, result.output)

console.print(Panel(Markdown(article.content), title="Article", border_style="cyan"))
console.print()

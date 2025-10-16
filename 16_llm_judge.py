#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "rich==14.2.0",
# ]
# ///
"""
Output Validation with Retry

Demonstrates using output_validator to enforce criteria and automatically retry
when outputs don't meet requirements. Simpler than using a separate judge agent.
"""

import os
import re

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent, ModelRetry
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

agent = Agent(
    model,
    system_prompt="You write LinkedIn posts about professional updates and achievements.",
    retries=3,
    instrument=True,
)


@agent.output_validator
def validate_linkedin_post(post: str) -> str:
    """Validate that post meets LinkedIn cringey standards."""

    emoji_count = len(re.findall(r"[\U0001F300-\U0001F9FF]", post))
    humble_brags = sum(
        1 for phrase in ["thrilled", "honored", "grateful", "humbled", "blessed"] if phrase.lower() in post.lower()
    )
    superlatives = sum(
        1 for word in ["amazing", "incredible", "fantastic", "awesome", "outstanding"] if word.lower() in post.lower()
    )

    logfire.info(f"Validation check: emojis={emoji_count}, humble_brags={humble_brags}, superlatives={superlatives}")

    issues = []
    if emoji_count < 3:
        issues.append(f"Need at least 3 emojis (found {emoji_count})")
    if humble_brags < 2:
        issues.append(f"Need at least 2 humble brag phrases (found {humble_brags})")
    if superlatives < 2:
        issues.append(f"Need at least 2 superlatives (found {superlatives})")

    if issues:
        feedback = ". ".join(issues)
        logfire.warn(f"Post rejected: {feedback}")
        raise ModelRetry(f"Post doesn't meet LinkedIn standards. {feedback}. Add more LinkedIn clichés.")

    logfire.info("Post approved!")
    return post


console.print("\n[bold cyan]LinkedIn Post Generator with Output Validation[/bold cyan]\n")

result = agent.run_sync("Write a post about getting promoted to senior engineer")
post = result.output

console.print(Panel(Markdown(post), title="Final Post", border_style="green"))
console.print(f"\n[dim]Took {len(result.all_messages())} messages (includes retries)[/dim]\n")

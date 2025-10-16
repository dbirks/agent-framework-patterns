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
LLM as Judge

Demonstrates using a smaller, faster LLM to validate outputs from another agent.
The judge enforces specific criteria and provides feedback for iterative improvement.
"""

import os
from textwrap import dedent
from typing import cast

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()


class LinkedInJudgment(BaseModel):
    approved: bool = Field(description="Whether the post meets LinkedIn standards")
    emoji_count: int = Field(description="Number of emojis found", ge=0)
    has_humble_brag: bool = Field(description="Contains humble brag phrases")
    has_superlatives: bool = Field(description="Contains superlatives like 'amazing', 'incredible'")
    feedback: str = Field(description="Specific feedback for improvement")


writer_agent = Agent(
    model,
    system_prompt="You write LinkedIn posts about professional updates and achievements.",
    instrument=True,
)

judge_agent = Agent(
    "anthropic:claude-haiku-4-5",
    output_type=LinkedInJudgment,
    system_prompt=dedent(
        """
        You're a LinkedIn content validator. Posts must have all of these:
        - At least 10 emojis
        - At least 3 humble brag phrases
        - At least 3 superlatives

        Only approve if all criteria are met. Be specific in feedback about what's missing.
        """
    ).strip(),
    instrument=True,
)

console.print("\n[bold cyan]LinkedIn Post Generator with LLM Judge[/bold cyan]\n")

topic = "Write a post about getting promoted to senior engineer"
max_attempts = 3
feedback = ""

logfire.info(f"Starting LinkedIn post generation with {max_attempts} max attempts")

for attempt in range(1, max_attempts + 1):
    logfire.info(f"Attempt {attempt}/{max_attempts}")
    console.print(f"[bold yellow]Attempt {attempt}/{max_attempts}[/bold yellow]\n")

    if attempt == 1:
        prompt = topic
    else:
        prompt = f"{topic}\n\nPrevious attempt was rejected. Improve it based on this feedback:\n{feedback}"
        logfire.info(f"Using feedback from previous attempt: {feedback}")

    logfire.info("Generating post with writer agent")
    result = writer_agent.run_sync(prompt)
    post = result.output

    console.print(Panel(Markdown(post), title=f"Draft {attempt}", border_style="blue"))

    logfire.info("Evaluating post with judge agent")
    judge_result = judge_agent.run_sync(f"Evaluate this LinkedIn post:\n\n{post}")
    judgment = cast(LinkedInJudgment, judge_result.output)

    logfire.info(
        f"Judge verdict: approved={judgment.approved}, emojis={judgment.emoji_count}, "
        f"humble_brag={judgment.has_humble_brag}, superlatives={judgment.has_superlatives}"
    )

    status = "✅ APPROVED" if judgment.approved else "❌ REJECTED"
    judge_output = f"""
**Status:** {status}

**Metrics:**
- Emojis: {judgment.emoji_count}
- Humble Brag: {"✅" if judgment.has_humble_brag else "❌"}
- Superlatives: {"✅" if judgment.has_superlatives else "❌"}

**Feedback:** {judgment.feedback}
"""

    console.print(
        Panel(Markdown(judge_output), title="Judge Evaluation", border_style="green" if judgment.approved else "red")
    )

    if judgment.approved:
        logfire.info(f"Post approved after {attempt} attempt(s)")
        console.print(f"\n[bold green]Post approved after {attempt} attempt(s)![/bold green]\n")
        break

    logfire.warn(f"Post rejected on attempt {attempt}: {judgment.feedback}")
    feedback = judgment.feedback
    console.print()
else:
    logfire.error(f"Failed to meet criteria after {max_attempts} attempts")
    console.print(f"\n[bold red]Failed to meet criteria after {max_attempts} attempts[/bold red]\n")

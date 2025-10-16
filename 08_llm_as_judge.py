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
LLM as Judge with Output Validator

Demonstrates using a smaller, faster LLM (Haiku) as a judge to validate outputs
from another agent. The judge enforces criteria and provides feedback for automatic
retries. Shows the output_validator pattern combined with LLM-as-judge.
"""

import os
from textwrap import dedent

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry
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
    humble_brag_count: int = Field(description="Number of humble brag phrases found", ge=0)
    superlatives_count: int = Field(description="Number of superlatives found", ge=0)
    hashtag_count: int = Field(description="Number of hashtags found", ge=0)
    feedback: str = Field(description="Specific feedback about what's missing or why it was approved")


# Judge agent using fast Haiku model
judge_agent = Agent[None, LinkedInJudgment](
    "anthropic:claude-haiku-4-5",
    output_type=LinkedInJudgment,
    system_prompt=dedent(
        """
        You're a LinkedIn content validator. Posts must have ALL of these:
        - At least 10 emojis
        - At least 3 humble brag phrases
        - At least 3 superlatives
        - At least 30 hashtags

        Count each criterion carefully. Only approve if ALL criteria are met.
        Be specific in feedback about what's missing or what was good.
        """
    ).strip(),
    instrument=True,
)

# Main writer agent
writer_agent = Agent(
    model,
    system_prompt="You write LinkedIn posts about professional updates and achievements. Use proper markdown formatting with bullet points on separate lines (- item or * item, each on its own line).",
    output_retries=10,
    instrument=True,
)


@writer_agent.output_validator
def validate_with_judge(post: str) -> str:
    """Use LLM judge to validate the post meets LinkedIn standards."""

    logfire.info("Calling judge agent to evaluate post")

    # Show the post being judged
    console.print(Panel(Markdown(post), title="Draft Post", border_style="blue"))

    # Call the judge agent to evaluate
    judge_result = judge_agent.run_sync(f"Evaluate this LinkedIn post:\n\n{post}")
    judgment = judge_result.output

    # Log the judgment
    logfire.info(
        f"Judge verdict: approved={judgment.approved}, emojis={judgment.emoji_count}, "
        f"humble_brags={judgment.humble_brag_count}, superlatives={judgment.superlatives_count}, "
        f"hashtags={judgment.hashtag_count}"
    )

    # Display judgment in console
    status = "✅ APPROVED" if judgment.approved else "❌ REJECTED"
    judge_output = dedent(
        f"""
        **Status:** {status}

        **Metrics:**
        - Emojis: {judgment.emoji_count}/10
        - Humble Brags: {judgment.humble_brag_count}/3
        - Superlatives: {judgment.superlatives_count}/3
        - Hashtags: {judgment.hashtag_count}/30

        **Feedback:** {judgment.feedback}
        """
    ).strip()

    console.print(
        Panel(
            Markdown(judge_output),
            title="Judge Evaluation",
            border_style="green" if judgment.approved else "red",
        )
    )

    if not judgment.approved:
        raise ModelRetry(f"Post rejected. {judgment.feedback}")

    logfire.info("Post approved by judge")
    return post


console.print("\n[bold cyan]LinkedIn Post with LLM Judge Validation[/bold cyan]\n")

result = writer_agent.run_sync("Write a simple, understated post about getting promoted to mid-level engineer")
post = result.output

console.print(Panel(Markdown(post), title="Final Approved Post", border_style="green"))
console.print(f"\n[dim]Took {len(result.all_messages())} messages (includes retries)[/dim]\n")

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
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")


# Structured output for final decision
class Decision(BaseModel):
    recommendation: str = Field(description="Final recommendation (approve, reject, or conditional)")
    rationale: str = Field(description="Reasoning behind the decision")
    key_benefits: list[str] = Field(description="Main benefits identified")
    key_risks: list[str] = Field(description="Main risks identified")
    conditions: list[str] = Field(description="Conditions or mitigations if applicable")


# Create agents with different perspectives
optimist_agent = Agent(
    model,
    system_prompt="""You're an optimistic strategist who focuses on opportunities and benefits.
Your role is to advocate for progress and innovation, highlighting potential gains and positive outcomes.
Be enthusiastic but still rational. Provide specific examples of benefits.""",
)

pessimist_agent = Agent(
    model,
    system_prompt="""You're a risk-focused analyst who identifies potential problems and challenges.
Your role is to ensure thorough consideration of downsides, risks, and obstacles.
Be critical but constructive. Provide specific examples of risks.""",
)

pragmatist_agent = Agent(
    model,
    system_prompt="""You're a pragmatic consultant who focuses on practical implementation.
Your role is to consider feasibility, costs, resources, and real-world constraints.
Be balanced and focus on what's actually achievable. Provide specific practical considerations.""",
)

judge_agent = Agent(
    model,
    output_type=Decision,
    system_prompt="""You're an impartial decision-maker who synthesizes multiple perspectives.
Evaluate all arguments fairly and provide a balanced final recommendation.
Consider benefits, risks, and practical constraints. Your decision should be well-reasoned and actionable.""",
)


def run_debate(topic: str, rounds: int = 2) -> Decision:
    """Run a multi-agent debate with multiple rounds."""

    print(f"🎭 DEBATE TOPIC: {topic}")
    print("=" * 70 + "\n")

    # Track conversation history for each agent
    optimist_history = []
    pessimist_history = []
    pragmatist_history = []

    # Run debate rounds
    for round_num in range(1, rounds + 1):
        print(f"{'=' * 70}")
        print(f"🔄 ROUND {round_num}")
        print(f"{'=' * 70}\n")

        # Optimist's turn
        print("😊 OPTIMIST:")
        optimist_prompt = f"Argue in favor of: {topic}"
        if optimist_history:
            optimist_prompt += f"\n\nRespond to previous points raised by others."

        optimist_result = optimist_agent.run_sync(
            optimist_prompt, message_history=optimist_history if optimist_history else None
        )
        optimist_view = optimist_result.output
        optimist_history.extend(optimist_result.new_messages())
        print(f"{optimist_view}\n")

        # Pessimist's turn (can see optimist's argument)
        print("😟 PESSIMIST:")
        pessimist_prompt = (
            f"Identify risks and challenges with: {topic}\n\nConsider this optimistic view:\n{optimist_view}"
        )
        if pessimist_history:
            pessimist_prompt += "\n\nBuild on your previous arguments."

        pessimist_result = pessimist_agent.run_sync(
            pessimist_prompt, message_history=pessimist_history if pessimist_history else None
        )
        pessimist_view = pessimist_result.output
        pessimist_history.extend(pessimist_result.new_messages())
        print(f"{pessimist_view}\n")

        # Pragmatist's turn (can see both arguments)
        print("🤔 PRAGMATIST:")
        pragmatist_prompt = f"""Provide a practical analysis of: {topic}

Optimistic perspective: {optimist_view}

Risk perspective: {pessimist_view}"""
        if pragmatist_history:
            pragmatist_prompt += "\n\nRefine your practical assessment."

        pragmatist_result = pragmatist_agent.run_sync(
            pragmatist_prompt, message_history=pragmatist_history if pragmatist_history else None
        )
        pragmatist_view = pragmatist_result.output
        pragmatist_history.extend(pragmatist_result.new_messages())
        print(f"{pragmatist_view}\n")

    # Judge synthesizes all perspectives
    print("=" * 70)
    print("⚖️  JUDGE'S DECISION")
    print("=" * 70 + "\n")

    judge_prompt = f"""Based on this debate about "{topic}", provide your final decision.

OPTIMIST'S PERSPECTIVE:
{optimist_view}

PESSIMIST'S PERSPECTIVE:
{pessimist_view}

PRAGMATIST'S PERSPECTIVE:
{pragmatist_view}

Synthesize these viewpoints into a balanced, actionable decision."""

    judge_result = judge_agent.run_sync(judge_prompt)
    decision: Decision = judge_result.output

    return decision


# Run debate demo
print("🏛️  Multi-Agent Debate Demo")
print("=" * 70)
print("Multiple agents with different perspectives debate to reach a decision\n")

topic = "Adopting AI code assistants across the engineering team"

decision = run_debate(topic, rounds=2)

# Display final decision
print(f"📋 RECOMMENDATION: {decision.recommendation.upper()}")
print(f"\n💭 RATIONALE:\n{decision.rationale}\n")

print("✅ KEY BENEFITS:")
for benefit in decision.key_benefits:
    print(f"   • {benefit}")

print("\n⚠️  KEY RISKS:")
for risk in decision.key_risks:
    print(f"   • {risk}")

if decision.conditions:
    print("\n📝 CONDITIONS/MITIGATIONS:")
    for condition in decision.conditions:
        print(f"   • {condition}")

print("\n" + "=" * 70)
print("✅ Multi-Agent Debate Benefits:")
print("   - Explores multiple perspectives systematically")
print("   - Reduces bias through diverse viewpoints")
print("   - Produces more balanced, thoughtful decisions")
print("   - Useful for strategic planning, risk assessment, decision-making")

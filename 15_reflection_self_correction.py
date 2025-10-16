#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///
"""
Reflection and Self-Correction

Demonstrates agents that critique and improve their own outputs through iterative refinement.
The agent generates an initial response, reflects on its quality, and produces an improved version.
Useful for tasks requiring high quality output or multiple revision cycles.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")


# Structured output for critique
class Critique(BaseModel):
    score: int = Field(description="Quality score from 1-10", ge=1, le=10)
    strengths: list[str] = Field(description="What the explanation does well")
    weaknesses: list[str] = Field(description="Areas that need improvement")
    suggestions: str = Field(description="Specific suggestions for improvement")


# Create specialized agents
writer_agent = Agent(
    model,
    system_prompt="""You're a technical writer who creates clear, engaging explanations of programming concepts.
Your explanations should be accurate, well-structured, and include examples.""",
)

critic_agent = Agent(
    model,
    output_type=Critique,
    system_prompt="""You're an expert editor who evaluates technical writing.
Evaluate explanations on:
- Clarity and accessibility
- Technical accuracy
- Use of examples
- Overall engagement
Provide constructive feedback for improvement.""",
)

print("🔄 Reflection & Self-Correction Demo")
print("=" * 70)
print("Writer generates → Critic evaluates → Writer improves iteratively\n")

topic = "Python decorators"
max_iterations = 3

print(f"📝 Topic: {topic}\n")

# Initial generation
print("=" * 70)
print("ITERATION 1: Initial Draft")
print("=" * 70)
result = writer_agent.run_sync(f"Explain {topic} in a clear, engaging way with an example.")
current_explanation = result.output
print(f"\n📄 Draft:\n{current_explanation}\n")

# Iterative improvement
for iteration in range(2, max_iterations + 1):
    # Critique current version
    print(f"{'=' * 70}")
    print(f"🔍 Critic Feedback (Iteration {iteration - 1}):")
    critique_result = critic_agent.run_sync(f"Evaluate this explanation of {topic}:\n\n{current_explanation}")
    critique: Critique = critique_result.output

    print(f"   Score: {critique.score}/10")
    print(f"   Strengths: {', '.join(critique.strengths)}")
    print(f"   Weaknesses: {', '.join(critique.weaknesses)}")
    print(f"   Suggestions: {critique.suggestions}\n")

    # Stop if quality is good enough
    if critique.score >= 8:
        print(f"✅ Quality threshold reached (score: {critique.score}/10)")
        break

    # Improve based on feedback
    print(f"{'=' * 70}")
    print(f"ITERATION {iteration}: Improved Draft")
    print(f"{'=' * 70}")

    improvement_prompt = f"""Improve this explanation of {topic} based on the following feedback:

Original explanation:
{current_explanation}

Feedback:
- Strengths: {", ".join(critique.strengths)}
- Weaknesses: {", ".join(critique.weaknesses)}
- Suggestions: {critique.suggestions}

Create an improved version that addresses the weaknesses while maintaining the strengths."""

    result = writer_agent.run_sync(improvement_prompt)
    current_explanation = result.output
    print(f"\n📄 Improved Draft:\n{current_explanation}\n")

# Final critique
print(f"{'=' * 70}")
print("🏆 Final Evaluation:")
final_critique_result = critic_agent.run_sync(f"Evaluate this final explanation of {topic}:\n\n{current_explanation}")
final_critique: Critique = final_critique_result.output
print(f"   Final Score: {final_critique.score}/10")
print(f"   Strengths: {', '.join(final_critique.strengths)}")

print(f"\n{'=' * 70}")
print("✅ Reflection Pattern Benefits:")
print("   - Iterative quality improvement")
print("   - Structured feedback for targeted improvements")
print("   - Self-correction without human intervention")
print("   - Useful for content generation, code review, analysis")

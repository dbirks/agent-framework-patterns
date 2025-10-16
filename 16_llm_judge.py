#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///
"""
LLM as Judge

Demonstrates using an LLM to evaluate and score outputs from other agents or models.
A judge agent provides objective assessment with structured criteria and scoring.
Useful for quality assurance, A/B testing, and automated evaluation of agent outputs.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")


# Structured output for judgement
class Judgment(BaseModel):
    approved: bool = Field(description="Whether the content meets all criteria")
    score: int = Field(description="Overall quality score from 1-10", ge=1, le=10)
    criteria_met: dict[str, bool] = Field(description="Which specific criteria were met")
    rejection_reasons: list[str] = Field(description="Reasons for rejection if not approved")
    suggestions: str = Field(description="Suggestions for improvement if not approved")


# Content generation agent
content_agent = Agent(
    model,
    system_prompt="You're a marketing copywriter creating product descriptions that are engaging and persuasive.",
)

# Judge agent with strict criteria
judge_agent = Agent(
    model,
    output_type=Judgment,
    system_prompt="""You're a quality assurance judge for product descriptions.
Evaluate content based on these criteria:
1. Length: 50-150 words
2. Tone: Professional yet friendly
3. Value proposition: Clearly states benefits
4. Call to action: Includes compelling CTA
5. Brand compliance: No superlatives like "best", "perfect", "revolutionary"

Only approve if ALL criteria are met.""",
)


def generate_with_validation(product: str, max_attempts: int = 3) -> tuple[str, list[Judgment]]:
    """Generate content with LLM judge validation and retry logic."""

    print(f"🎯 Generating description for: {product}")
    print(f"   Max attempts: {max_attempts}\n")

    judgments = []
    current_content = None
    feedback_context = ""

    for attempt in range(1, max_attempts + 1):
        print(f"{'=' * 70}")
        print(f"Attempt {attempt}/{max_attempts}")
        print(f"{'=' * 70}\n")

        # Generate content (incorporating previous feedback if any)
        prompt = f"Create a compelling product description for: {product}"
        if feedback_context:
            prompt += f"\n\nPrevious attempt was rejected. Improve based on this feedback:\n{feedback_context}"

        result = content_agent.run_sync(prompt)
        current_content = result.output

        print(f"📝 Generated Content:\n{current_content}\n")

        # Judge the content
        print("⚖️  Evaluating with LLM judge...")
        judge_result = judge_agent.run_sync(f"Evaluate this product description:\n\n{current_content}")
        judgment: Judgment = judge_result.output
        judgments.append(judgment)

        # Display judgment
        print(f"   Score: {judgment.score}/10")
        print(f"   Approved: {'✅ YES' if judgment.approved else '❌ NO'}")
        print(f"   Criteria Met:")
        for criterion, met in judgment.criteria_met.items():
            status = "✅" if met else "❌"
            print(f"      {status} {criterion}")

        if judgment.approved:
            print(f"\n🎉 Content approved on attempt {attempt}!")
            return current_content, judgments

        # Prepare feedback for next iteration
        print(f"\n   Rejection Reasons:")
        for reason in judgment.rejection_reasons:
            print(f"      • {reason}")
        print(f"\n   Suggestions: {judgment.suggestions}\n")

        feedback_context = f"""
Rejection reasons: {", ".join(judgment.rejection_reasons)}
Suggestions: {judgment.suggestions}
"""

    print(f"\n⚠️  Failed to meet criteria after {max_attempts} attempts")
    return current_content, judgments


# Demo: Generate product descriptions with validation
print("⚖️  LLM Judge & Validation Demo")
print("=" * 70)
print("Content is generated and validated against strict criteria\n")

products = [
    "Wireless Bluetooth Headphones with noise cancellation",
    "Organic Green Tea Blend with Jasmine",
]

for product in products:
    print("\n" + "=" * 70)
    print(f"PRODUCT: {product}")
    print("=" * 70 + "\n")

    final_content, all_judgments = generate_with_validation(product, max_attempts=3)

    print(f"\n{'=' * 70}")
    print(f"📊 Summary:")
    print(f"   Total attempts: {len(all_judgments)}")
    print(f"   Final score: {all_judgments[-1].score}/10")
    print(f"   Status: {'✅ Approved' if all_judgments[-1].approved else '❌ Not Approved'}")
    print("\n")

print("=" * 70)
print("✅ LLM Judge Pattern Benefits:")
print("   - Automated quality assurance")
print("   - Consistent evaluation against criteria")
print("   - Retry logic with targeted feedback")
print("   - Useful for content moderation, brand compliance, quality control")
